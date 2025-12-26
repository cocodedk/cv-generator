"""Create profile from data."""
from typing import Dict, Any
from backend.database.queries.profile import save_profile


def create_profile(profile_data: Dict[str, Any]) -> bool:
    """Create profile in database from profile data.

    Args:
        profile_data: Dictionary containing personal_info, experience,
                     education, and skills

    Returns:
        True if profile was created successfully, False otherwise
    """
    try:
        print("Creating profile from docs/me.md data...")
        result = save_profile(profile_data)

        if result:
            print("✅ Profile created successfully!")
            print(f"   Name: {profile_data['personal_info']['name']}")
            print(f"   Email: {profile_data['personal_info']['email']}")
            print(f"   Experiences: {len(profile_data['experience'])}")
            print(f"   Education: {len(profile_data['education'])}")
            print(f"   Skills: {len(profile_data['skills'])}")
            return True
        else:
            print("❌ Failed to create profile")
            return False

    except Exception as e:
        print(f"❌ Error creating profile: {e}")
        import traceback
        traceback.print_exc()
        return False
