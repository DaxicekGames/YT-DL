import yt_dlp

def format(formats):
    print("\nAvalible resolutions (mp4):")
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
            choice_prompt = input('\nEnter resolution number (type "all" for all avalible formats): ')
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

def yt_download(url: str, typ: str, info):
    if typ == None: typ = "v"

    ydl_opts = {}

    try:
        with yt_dlp.YoutubeDL() as ydl:

            # Kontrola, zda jde o playlist nebo jedno video
            if 'entries' in info:
                print(f"Processing playlist: {info['title']}")
                videos = info['entries']
            else:
                videos = [info]  # Pokud je to jedno video

            for video in videos:

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
    print("""
    ╔═══════════════════YT-DL═══════════════════╗
    ║Download Youtube videos in high resolution!║
    ║                                           ║
    ║Created by: Daxicek                        ║
    ║Using: yt_dlp, FFmpeg                      ║
    ╚═══════════════════════════════════════════╝
          """)
    

    url = input("Enter video or playlist URL: ")
    while url != "":
        print("Loading info...")
        video_info = yt_dlp.YoutubeDL().extract_info(url, download=False)
        title_info = video_info['title']

        title_len = int(len(title_info)) if len(title_info) % 2 == 0 else int(len(title_info)+1)
        title = "    ╔"
        for _ in range(int(title_len/2)-2): title += "═"
        title += "TITLE"
        for _ in range(int(title_len/2)-3): title += "═"
        title += "╗\n"
        title += "    ║" + title_info if len(title_info) % 2 == 0 else ("    ║" + title_info + " ")
        title += "║\n" + "    ╚"
        for _ in range(title_len): title += "═"
        title += "╝"

        print(f"\n{title}\n")

        typ = input("Do you want to download [v]ideo or [a]udio: ")
        
        yt_download(url, typ, video_info)

        url = input("\nEnter video or playlist URL (press enter to exit): ")


if __name__ == "__main__":
    main()
