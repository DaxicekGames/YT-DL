try:
    import yt_dlp
    import ffmpeg
    import os
    import re
except:
    input('Missing dependencies... \nIf you are running thist program for the first time, run "INSTALL DEPENDENCIES.bat" first!\nMake sure to run this program using "RUN.bat" or command line\n(press Enter to exit)')
    quit()

preffered_acodec = "mp3"
keep_format = False
kept_format = None

def file_name_lagalizer(text):
    # Regulární výraz: povolena čísla, písmena s diakritikou, závorky a tečky
    pattern = r'[^0-9a-zA-Zá-žÁ-Ž().\-\s]'
    # Nahraď vše, co neodpovídá povoleným znakům, prázdným řetězcem
    out_text = re.sub(pattern, '', text)
    return out_text

def convert_acodec(input_file, output_file, target_codec):
    print("Starting audio codec convertion...")

    # Načtení vstupního videa
    stream = ffmpeg.input(input_file)
    
    # Nastavení zvukového kodeku na nový (výchozí: mp3)
    stream = ffmpeg.output(stream, output_file, acodec=target_codec, vcodec='copy')
    
    # Spuštění převodu
    ffmpeg.run(stream, quiet=True)
    
    print(f"Audio codec convertion completed!")

def format(formats):
    global keep_format, kept_format, preffered_acodec

    prev_res = None
    basic_formats = {0:0}
    basic_choice = True

    if kept_format != None:
        for i, format in enumerate(formats):  
            if format['format_id'] == kept_format:
                return kept_format
    print("\nAvalible resolutions (mp4):")
    for i, format in enumerate(formats):
        if format['vcodec'] != 'none' and "mp4" in format['ext'] and "p" in format['format'] and prev_res != format['resolution']:  # Formáty s videem
            print(f"{(list(basic_formats.values())[-1]+1)}: {format['format']}")
            prev_res = format['resolution']
            basic_formats.update({(i+1):(list(basic_formats.values())[-1]+1)})

    
    while True:
        choice_prompt = input('\nEnter resolution number (type "all" for all avalible formats and to choose audio codec): ')
        choice_prompt = choice_prompt.split(" ")

        try:
            if choice_prompt[0] != "all": int(choice_prompt[0])

            if choice_prompt[0].lower() == "all":
                basic_choice = False
                for i, format in enumerate(formats):  
                    print(f"{i + 1}: {format['format']} - {format['resolution']} ({format['ext']})")
                print("\nAudio codecs (seperate by space):\n1: mp3 (reccomended, default)\n2: aac\n3: No convertion - Opus (fastest, not widely supported)")
            elif basic_choice == False:
                choice = int(choice_prompt[0]) - 1
                try:
                    match choice_prompt[1]:
                        case "1":
                            preffered_acodec = "mp3"
                        case "2":
                            preffered_acodec = "aac"
                        case "3":
                            preffered_acodec = "opus"
                        case _:
                            preffered_acodec = "mp3"
                except: ...

                if keep_format: kept_format = formats[choice]['format_id']
                keep_format = False
                return formats[choice]['format_id']

            else:
                choice = int(list(basic_formats.keys())[list(basic_formats.values()).index(int(choice_prompt[0]))]) - 1
                if keep_format: kept_format = formats[choice]['format_id']
                keep_format = False

                return formats[choice]['format_id']
        except:
            print("Invalid selection! Try again...")





def yt_download(typ: str, info):
    global keep_format
    need_convert_acodec = False
    

    ydl_opts = {}

    try:
        with yt_dlp.YoutubeDL() as ydl:

            # Kontrola, zda jde o playlist nebo jedno video
            if 'entries' in info:
                print(f"Processing playlist: {info['title']}")
                videos = info['entries']
                keep_format = True
            else:
                videos = [info]  # Pokud je to jedno video

            for video in videos:

                match typ:
                    case 'v':
                        need_convert_acodec = True
                        # Výpis dostupných formátů
                        format_id = format(video['formats'])
                        # Stáhnout nejlepší video i audio a sloučit je dohromady
                        ydl_opts = {'format': f'{format_id}+bestaudio', 'merge_output_format': 'mp4', 'outtmpl': 'temp.mp4'}
                    case 'a':
                        # Pouze audio
                        ydl_opts = {'format': 'bestaudio', 'outtmpl': file_name_lagalizer(video['title']), 'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]}

                # Spustit stažení jednotlivých videí nebo audia
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video['webpage_url']])
                print(f"Download has finished: {video['title']}")
                
                if preffered_acodec == "opus":
                    os.rename("temp.mp4", f"{file_name_lagalizer(video['title'])}.mp4")
                elif need_convert_acodec:
                    convert_acodec("temp.mp4", f"{file_name_lagalizer(video['title'])}.mp4", preffered_acodec)
                    os.remove("temp.mp4")

    except Exception as e:
        print(f"Error occured: {e}")

def main():
    global keep_format, kept_format

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
        try:
            video_info = yt_dlp.YoutubeDL().extract_info(url, download=False)
            title_info = video_info['title']

            title_len = int(len(title_info)) if len(title_info) % 2 == 0 else int(len(title_info)+1)
            title = "    ╔"
            for _ in range(int(title_len/2)-2): title += "═"
            title += "VIDEO"
            for _ in range(int(title_len/2)-3): title += "═"
            title += "╗"
            title += "\n    ║" + title_info if len(title_info) % 2 == 0 else ("\n    ║" + title_info + " ")
            title += "║\n" + "    ╚"
            for _ in range(title_len): title += "═"
            title += "╝"

            print(f"\n{title}\n")

            typ = input("Do you want to download [v]ideo or [a]udio: ")
            if (typ == "") or (typ.lower()[0] != "a" and typ.lower()[0] != "v"): typ = "v"
            
            yt_download(typ, video_info)
        except: 
            print("\nSomething went wrong, please try again...")

        keep_format = False
        kept_format = None
        url = input("\nEnter video or playlist URL (press enter to exit): ")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
