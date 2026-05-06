import requests

TOKEN = 'YOUR_GITHUB_TOKEN'
URL = 'https://api.github.com/graphql'

def calculate_level(stats):
    """
    Calculates XP and Rank based on contribution metrics.
    Weights: PRs (5), Reviews (4), Commits (1), Issues (1), Stars (2)
    """
    # Extract data with defaults to avoid errors
    commits = stats.get('totalCommitContributions', 0)
    prs = stats.get('totalPullRequestContributions', 0)
    issues = stats.get('totalIssueContributions', 0)
    reviews = stats.get('totalPullRequestReviewContributions', 0)
    stars = stats.get('stars', 0)

    # Calculate total XP
    xp = (commits * 1) + (prs * 5) + (reviews * 4) + (issues * 1) + (stars * 2)

    # Rank Thresholds
    if xp >= 1000: rank = "S (Grandmaster)"
    elif xp >= 500: rank = "A (Expert)"
    elif xp >= 200: rank = "B (Contributor)"
    elif xp >= 50:  rank = "C (Novice)"
    else:           rank = "D (Beginner)"

    return rank, xp

def get_user_dashboard(username):
    # Added 'totalPullRequestReviewContributions' and a nested star count
    query = """
    query($login: String!) {
      user(login: $login) {
        name
        followers { totalCount }
        repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC) {
          nodes {
            stargazerCount
          }
        }
        contributionsCollection {
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
        }
      }
    }
    """
    
    variables = {"login": username}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = requests.post(URL, json={'query': query, 'variables': variables}, headers=headers)
    
    if response.status_code == 200:
        res_json = response.json()
        if not res_json.get('data') or not res_json['data']['user']:
            print("User not found.")
            return

        user_data = res_json['data']['user']
        stats = user_data['contributionsCollection']
        
        # Calculate total stars across all public owned repos
        total_stars = sum(repo['stargazerCount'] for repo in user_data['repositories']['nodes'])
        stats['stars'] = total_stars # Injecting stars into stats for the level calculator

        # Get the level
        rank, xp = calculate_level(stats)
        density = stats['totalCommitContributions'] / max(stats['totalPullRequestContributions'], 1)
        
        print(f"--- {username}'s Developer Dashboard ---")
        print(f"Real Name:    {user_data['name']}")
        print(f"Total XP:     {xp}")
        print(f"Current Rank: {rank}")
        print("-" * 30)
        print(f"Commits:      {stats['totalCommitContributions']}")
        print(f"PRs Opened:   {stats['totalPullRequestContributions']}")
        print(f"Code Reviews: {stats['totalPullRequestReviewContributions']}")
        print(f"Issues:       {stats['totalIssueContributions']}")
        print(f"Stars Earned: {total_stars}")
        print(f"Followers:    {user_data['followers']['totalCount']}")
        print(f"Commit Density: {density:.1f} commits per PR")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    get_user_dashboard("your username here")
