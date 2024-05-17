def manage(sp, message, playback):
    playback = sp.current_playback()
    artist_id = playback["item"]["artists"][0]["id"]
    artist_name = playback["item"]["artists"][0]["name"]
    
    if "follow_or_unfollow_artist" in message or "toggle_follow" in message:
        results = sp.search(q=artist_name, type="artist")
        items = results["artists"]["items"]
        if items:
            artist_id = items[0]["id"]
        else:
            print(f"Unable to find artist '{artist_name}' on Spotify.")

        # Check if the user is subscribed to the corresponding artist
        is_following = sp.current_user_following_artists(ids=[artist_id])[0]
        if is_following:
            print(f"The user is subscribed to the artist '{artist_name}'.")
            sp.user_unfollow_artists([artist_id])
            print("The artist has been removed from the subscription list.")
        else:
            print(f"The user is not subscribed to the artist '{artist_name}'.")
            sp.user_follow_artists([artist_id])
            print("The artist has been added to the subscription list.")

    elif "unfollow_artist" in message:
        sp.user_unfollow_artists([artist_id])
        print("The artist has been removed from the subscription list.")
        
    elif "follow_artist" in message:
        sp.user_follow_artists([artist_id])
        print("The artist has been added to the subscription list.")