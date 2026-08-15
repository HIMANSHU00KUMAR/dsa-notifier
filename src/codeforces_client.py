import random
import logging
from typing import Dict, List, Optional, Set, Tuple, Any
import requests

logger = logging.getLogger(__name__)

CF_API_BASE = "https://codeforces.com/api"


class CodeforcesClient:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodeforcesDailyNotifier/1.0"
        })

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the Codeforces API with error handling."""
        url = f"{CF_API_BASE}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "OK":
                comment = data.get("comment", "Unknown Codeforces API error")
                raise RuntimeError(f"Codeforces API error ({endpoint}): {comment}")
            return data.get("result", {})
        except requests.RequestException as e:
            logger.error(f"Failed to connect to Codeforces API ({endpoint}): {e}")
            raise

    def get_user_info(self, handle: str) -> Optional[Dict[str, Any]]:
        """Fetch user profile information including rating and rank."""
        if not handle:
            return None
        try:
            result = self._get("user.info", {"handles": handle})
            if result and isinstance(result, list) and len(result) > 0:
                return result[0]
        except Exception as e:
            logger.warning(f"Could not fetch user info for '{handle}': {e}")
        return None

    def get_user_solved_problems(self, handle: str) -> Set[str]:
        """
        Fetch all problem keys solved by the user (verdict == OK).
        Returns a set of problem IDs like {'1872E', '1872D', ...}.
        """
        solved = set()
        if not handle:
            return solved

        try:
            logger.info(f"Fetching solved problems for handle '{handle}'...")
            submissions = self._get("user.status", {"handle": handle, "from": 1, "count": 10000})
            for sub in submissions:
                if sub.get("verdict") == "OK":
                    prob = sub.get("problem", {})
                    contest_id = prob.get("contestId")
                    index = prob.get("index")
                    if contest_id and index:
                        solved.add(f"{contest_id}{index.strip().upper()}")
            logger.info(f"User '{handle}' has solved {len(solved)} unique problems.")
        except Exception as e:
            logger.warning(f"Could not fetch submission history for '{handle}': {e}. Proceeding without solved filter.")
        return solved

    def get_problemset(self, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetch the problemset list, optionally filtered by tag."""
        params = {}
        if tags and len(tags) == 1:
            params["tags"] = tags[0]
        
        logger.info("Fetching global problemset from Codeforces...")
        data = self._get("problemset.problems", params)
        problems = data.get("problems", [])
        logger.info(f"Fetched {len(problems)} problems from Codeforces problemset.")
        return problems

    def select_daily_problem(
        self,
        handle: str = "",
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        preferred_tags: Optional[List[str]] = None,
        excluded_keys: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """
        Selects an unsolved, unrecommended problem matching the rating and tag criteria.
        """
        if excluded_keys is None:
            excluded_keys = set()

        # Step 1: Determine target rating range
        user_info = None
        current_rating = None
        if handle:
            user_info = self.get_user_info(handle)
            if user_info:
                current_rating = user_info.get("rating")
                logger.info(f"Found handle '{handle}' with rating: {current_rating}, rank: {user_info.get('rank')}")

        if min_rating is None and max_rating is None:
            if current_rating:
                # If rating is known, target [rating, rating + 200] (or at least 800)
                min_rating = max(800, (current_rating // 100) * 100)
                max_rating = min_rating + 300
            else:
                # Default beginner/intermediate range
                min_rating = 1000
                max_rating = 1400
        elif min_rating is None:
            min_rating = 800
        elif max_rating is None:
            max_rating = min_rating + 400

        logger.info(f"Target rating range: {min_rating} - {max_rating}")

        # Step 2: Fetch solved problems for handle
        solved_problems = self.get_user_solved_problems(handle)
        all_excluded = solved_problems.union(excluded_keys)

        # Step 3: Fetch candidate problems
        all_problems = self.get_problemset()

        preferred_tags_normalized = [t.strip().lower() for t in preferred_tags] if preferred_tags else []

        # Filter candidate pool
        candidates = []
        for prob in all_problems:
            contest_id = prob.get("contestId")
            index = prob.get("index")
            rating = prob.get("rating")
            tags = [t.lower() for t in prob.get("tags", [])]

            if not contest_id or not index or rating is None:
                continue

            key = f"{contest_id}{index.strip().upper()}"
            if key in all_excluded:
                continue

            if not (min_rating <= rating <= max_rating):
                continue

            if preferred_tags_normalized:
                # Check if at least one preferred tag matches
                if not any(pref in tags for pref in preferred_tags_normalized):
                    continue

            candidates.append(prob)

        logger.info(f"Found {len(candidates)} matching candidate problems.")

        # Fallback if no problems found with tag filter
        if not candidates and preferred_tags_normalized:
            logger.warning("No candidates found with tag filter. Falling back to rating-only filter.")
            for prob in all_problems:
                contest_id = prob.get("contestId")
                index = prob.get("index")
                rating = prob.get("rating")
                if not contest_id or not index or rating is None:
                    continue

                key = f"{contest_id}{index.strip().upper()}"
                if key in all_excluded:
                    continue

                if min_rating <= rating <= max_rating:
                    candidates.append(prob)
            logger.info(f"Found {len(candidates)} candidates after relaxing tag filter.")

        # Fallback if still empty (widen rating bracket)
        if not candidates:
            logger.warning("No candidates found in rating range. Widening rating search window.")
            for prob in all_problems:
                contest_id = prob.get("contestId")
                index = prob.get("index")
                rating = prob.get("rating")
                if not contest_id or not index or rating is None:
                    continue

                key = f"{contest_id}{index.strip().upper()}"
                if key in all_excluded:
                    continue

                if max(800, min_rating - 200) <= rating <= max_rating + 200:
                    candidates.append(prob)

        if not candidates:
            raise RuntimeError("No suitable Codeforces problem could be found matching the criteria.")

        # Select a problem (bias towards relatively newer contests for better quality & modern tests)
        # Sort candidates by contestId descending (higher contestId = newer)
        candidates.sort(key=lambda p: p.get("contestId", 0), reverse=True)
        # Pick randomly from the top 50 newest matching candidates
        top_candidates = candidates[:min(50, len(candidates))]
        selected = random.choice(top_candidates)

        contest_id = selected["contestId"]
        index = selected["index"].strip().upper()
        problem_key = f"{contest_id}{index}"
        
        # Build problem URL
        if contest_id >= 100000:
            url = f"https://codeforces.com/gym/{contest_id}/problem/{index}"
        else:
            url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"

        return {
            "key": problem_key,
            "contestId": contest_id,
            "index": index,
            "name": selected.get("name", "Unknown Problem"),
            "rating": selected.get("rating"),
            "tags": selected.get("tags", []),
            "url": url,
            "user_rating": current_rating,
            "target_range": f"{min_rating}-{max_rating}"
        }
