import json
import urllib.request
import os

URL = "https://raw.githubusercontent.com/ladyisatis/one-pace-metadata/v2/stremio/meta/series/pp_onepace.json"

def shift_season(id, current_s):
    """
    Maps the new 36-season numbering back to the 33-season format.
    """
    # 1. Handle the "Cover Stories" overrides
    if id == "TH_1": return 6  # Buggy's Crew -> Season 6
    if id == "TE_1": return 9  # Koby-Meppo -> Season 9
    if id == "IF_1": return 22 # Straw Hat Stories -> Season 22
    
    # 2. General Shifting Rules (36 -> 33)
    if current_s <= 6:
        return current_s
    elif current_s <= 7: 
        return 7
    elif current_s <= 10: 
        return current_s - 1
    elif current_s <= 24: 
        return current_s - 2
    else: 
        return current_s - 3

def clean_metadata():
    print("Fetching and re-mapping data...")
    try:
        with urllib.request.urlopen(URL) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        meta_obj = data.get('meta', data)
        unique_videos = []
        seen_ids = set()
        
        if 'videos' in meta_obj:
            for video in meta_obj['videos']:
                v_id = video['id']
                if v_id not in seen_ids:
                    seen_ids.add(v_id)
                    video.pop('released', None) # Remove crashing date

                    
                    if video.get('season') == 17:
                        video['episode'] = int(video['episode']) + 1

                    # --- Apply specific overrides ---
                    if v_id == "TH_1":
                        video['episode'] = 11
                        video['title'] = "[Cover Story] The Adventures of Buggy's Crew"
                    elif v_id == "TE_1":
                        video['episode'] = 3
                        video['title'] = "[Cover Story] The Trials of Koby-Meppo"
                    elif v_id == "IF_1":
                        video['episode'] = 11
                        video['title'] = "[Cover Story] The Adventures of the Straw Hats"

                    # --- Apply the Season Shifting ---
                    video['season'] = shift_season(v_id, video['season'])
                    
                    unique_videos.append(video)

            
            if "WN_1" not in seen_ids:
                print("[!] WN_1 missing from source. Injecting 'Onward to Wano'...")
                wano_start = {
                    "id": "WN_1",
                    "season": shift_season("WN_1", 35), # This will correctly become Season 32
                    "episode": 1,
                    "title": "Onward to Wano",
                    "overview": "The Straw Hats begin their infiltration of the isolated Land of Wano."
                }
                unique_videos.append(wano_start)
            
            # Sort videos by season and episode to make sure the injected WN_1 is in the right spot
            unique_videos.sort(key=lambda x: (x['season'], x['episode']))
            
            meta_obj['videos'] = unique_videos
            print(f"Cleaned! Total: {len(unique_videos)} episodes across 33 seasons.")
        
        final_data = {"meta": meta_obj}
        os.makedirs("src", exist_ok=True)
        with open("src/pp_onepace.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        print("Saved to src/pp_onepace.json")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    clean_metadata()
