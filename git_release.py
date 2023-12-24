import argparse
import requests

# Function to create or update a GitHub release
def create_github_release(token, owner, repo, tag_name, target_commitish, name, body, draft=False, prerelease=False, generate_release_notes=False):
    # Check if a release with the same tag already exists
    existing_release = get_existing_release(token, owner, repo, tag_name)

    if existing_release:
        print(f"Release with tag '{tag_name}' already exists.")
        print("Existing Release Details:")
        print(existing_release)
    else:
        # URL for creating a release
        release_url = f'https://api.github.com/repos/{owner}/{repo}/releases'

        # JSON data for the release
        release_data = {
            "tag_name": tag_name,
            "target_commitish": target_commitish,
            "name": name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease,
            "generate_release_notes": generate_release_notes
        }

        # Headers for the request
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Make the POST request to create the release
        response = requests.post(release_url, headers=headers, json=release_data)

        if response.status_code == 201:
            print(f"Release '{tag_name}' created successfully.")
            print("Release Creation Response:")
            print(response.text)
            # Return the release ID
            release_id = response.json().get('id')
            return release_id
        else:
            print(f"Error creating release '{tag_name}': {response.status_code}")
            print("Release Creation Response:")
            print(response.text)

    return None

# Function to get the ID of a release by tag name
def get_existing_release(token, owner, repo, tag_name):
    # URL for getting releases by tag name
    release_url = f'https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag_name}'

    # Headers for the request
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Make a GET request to check if the release exists
    response = requests.get(release_url, headers=headers)

    if response.status_code == 200:
        # Release with the same tag exists, return its details
        return response.json()
    else:
        # Release with the tag does not exist
        return None

# Function to upload a release asset
def upload_release_asset(token, owner, repo, release_id, asset_name, file_path):
    # URL for uploading a release asset
    asset_url = f'https://uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets?name={asset_name}'

    # Headers for the request
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Read the binary file
    with open(file_path, 'rb') as file:
        # Make a POST request to upload the asset
        response = requests.post(asset_url, headers=headers, data=file)

    if response.status_code == 201:
        print(f"Asset '{asset_name}' uploaded successfully.")
        print("Asset Upload Response:")
        print(response.text)
    else:
        print(f"Error uploading asset '{asset_name}': {response.status_code}")
        print("Asset Upload Response:")
        print(response.text)

def get_existing_release_asset(token, owner, repo, release_id, asset_name):
    # URL for getting release assets
    assets_url = f'https://api.github.com/repos/{owner}/{repo}/releases/{release_id}/assets'

    # Headers for the request
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Make a GET request to list release assets
    response = requests.get(assets_url, headers=headers)

    if response.status_code == 200:
        # Search for the asset by name
        assets = response.json()
        for asset in assets:
            if asset["name"] == asset_name:
                return asset
    return None

# Function to delete a release asset
def delete_release_asset(token, owner, repo, release_id, asset_name):
    existing_asset = get_existing_release_asset(token, owner, repo, release_id, asset_name)

    if existing_asset:
        asset_url = f'https://api.github.com/repos/{owner}/{repo}/releases/assets/{existing_asset["id"]}'
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Make a DELETE request to delete the asset
        response = requests.delete(asset_url, headers=headers)

        if response.status_code == 204:
            print(f"Asset '{asset_name}' deleted successfully.")
        else:
            print(f"Error deleting asset '{asset_name}': {response.status_code}")
            print("Asset Deletion Response:")
            print(response.text)
    else:
        print(f"Asset '{asset_name}' not found in the release.")

def main():
    parser = argparse.ArgumentParser(description="Create a GitHub release and upload an asset")
    parser.add_argument("--github_token", required=True, help="GitHub access token")
    parser.add_argument("--repository_owner", required=True, help="GitHub repository owner")
    parser.add_argument("--repository_name", required=True, help="GitHub repository name")
    parser.add_argument("--release_tag", required=True, help="Release tag")
    parser.add_argument("--new_release_name", required=True, help="New release name")
    parser.add_argument("--new_release_description", required=True, help="New release description")
    parser.add_argument("--file_path", required=True, help="Path to the file to upload")
    parser.add_argument("--file_name", required=True, help="Name for the uploaded file")

    args = parser.parse_args()

    # Create or check the release; get release id; upload using release id
    create_github_release(args.github_token, args.repository_owner, args.repository_name, args.release_tag, 'main',
                          args.new_release_name, args.new_release_description)
    r_id = get_existing_release(args.github_token, args.repository_owner, args.repository_name, args.release_tag)['id']

    # Check if the asset exists and get its name
    existing_asset = get_existing_release_asset(args.github_token, args.repository_owner, args.repository_name, r_id,
                                                args.file_name)
    if existing_asset:
        file_name_to_replace = existing_asset['name']
        # Delete the existing asset
        delete_release_asset(args.github_token, args.repository_owner, args.repository_name, r_id, file_name_to_replace)

    upload_release_asset(args.github_token, args.repository_owner, args.repository_name, r_id, args.file_name, args.file_path)

if __name__ == "__main__":
    main()
