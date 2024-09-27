import yt_dlp

def format(formats):
    print("\nAvalible resolution and format IDs:")
    prev_res = None
    basic_formats = {0:0}
    basic_choice = True
    for i, format in enumerate(formats):
        if format['vcodec'] != 'none' and "mp4" in format['ext'] and "p" in format['format'] and prev_res != format['resolution']:  # Formáty s videem
            print(f"{(list(basic_formats.values())[-1]+1)}: {format['format']}")
            prev_res = format['resolution']
            basic_formats.update({(i+1):(list(basic_formats.values())[-1]+1)})
    
    while True:
        try:
            choice_prompt = input('\nEnter format number (type "all" for all avalible formats): ')
            if choice_prompt.lower() == "all":
                basic_choice = False
                for i, format in enumerate(formats):  
                    print(f"{i + 1}: {format['format']} - {format['resolution']} ({format['ext']})")
            elif basic_choice == False:
                choice = int(choice_prompt) - 1
                if 0 <= choice < len(formats):
                    return formats[choice]['format_id']
                else:
                    if choice != 0:
                        print("Invalid selection, try again...")
            else:
                choice = int(list(basic_formats.keys())[list(basic_formats.values()).index(int(choice_prompt))]) - 1
                if 0 <= choice < len(formats):
                    return formats[choice]['format_id']
                else:
                    if choice != 0:
                        print("Invalid selection, try again...")
        except ValueError:
            print("Please enter valid number...")

def yt_download(url, typ):
    ydl_opts = {}

    try:
        with yt_dlp.YoutubeDL() as ydl:
            # Získání informací o videu nebo playlistu
            info = ydl.extract_info(url, download=False)

            # Kontrola, zda jde o playlist nebo jedno video
            if 'entries' in info:
                print(f"Processing playlist: {info['title']}")
                videos = info['entries']
            else:
                videos = [info]  # Pokud je to jedno video

            for video in videos:
                print(f"Downloading video: {video['title']}")

                match typ:
                    case 'v':
                        # Výpis dostupných formátů
                        format_id = format(video['formats'])
                        # Stáhnout nejlepší video i audio a sloučit je dohromady
                        ydl_opts = {'format': f'{format_id}+bestaudio', 'merge_output_format': 'mp4'}
                    case 'a':
                        # Pouze audio
                        ydl_opts = {'format': 'bestaudio', 'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]}
                    case _:
                        print("Invalid selection...")
                        return

                # Spustit stažení jednotlivých videí nebo audia
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video['webpage_url']])
                print(f"Download has finished: {video['title']}")

    except Exception as e:
        print(f"Error occured: {e}")

def main():
    url = input("Enter video or playlist URL: ")
    typ = input("Do you want to download [v]ideo or [a]udio: ").lower()[0]
    
    yt_download(url, typ)

if __name__ == "__main__":
    main()
