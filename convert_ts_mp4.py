from glob import glob, has_magic
from subprocess import run, CalledProcessError, DEVNULL
from pathlib import Path
from argparse import ArgumentParser
from typing import List

if __name__ == "__main__":
    parser = ArgumentParser(description="Convert or re-encode .TS file(s) to .MP4")
    parser.add_argument("files", nargs="*", help="(Required) List of files to convert")
    parser.add_argument("-r", "--reencode", action="store_true", help="(Optional) Re-encode the input files")
    parser.add_argument("-crf", type=int, default=23, help="(Optional) Set the constant rate factor for FFMpeg to use")
    parser.add_argument("--showoutput", action="store_true", help="(Optional) Show FFMpeg output while running")
    
    args = parser.parse_args()
    
    if not args.files:
        parser.error('No files provided. Please run with "--help" ("-h") for usage')
    
    FILES_TO_CONVERT: List[Path] = []
    for pattern in args.files:
        if has_magic(pattern):
            matches = [Path(p) for p in glob(pattern)]
            if not matches:
                parser.error(f"No files matched wildcard pattern: '{pattern}'")
        else:
            matches = [Path(pattern)]
        
        for path in matches:
            if not path.is_file():
                parser.error(f"File not found: '{path}'")
            if path.suffix.lower() != ".ts":
                parser.error(f"Invalid file type '{path.suffix}' for '{path}'. Expected '.ts' file(s)")
            if path not in FILES_TO_CONVERT:
                FILES_TO_CONVERT.append(path)
    
    FFMPEG_OUTPUT_TARGET = None if args.showoutput else DEVNULL

    for ts_file in FILES_TO_CONVERT:
        mp4_file = ts_file.with_suffix(".mp4")
        print(f"Converting {ts_file.name}")
        
        try:
            if args.reencode:
                command = [
                    "ffmpeg", "-i", str(ts_file.resolve()), "-c:v", "libx264", "-crf", str(args.crf), "-preset", "medium", 
                    "-c:a", "aac", "-b:a", "192k", "-y", str(mp4_file.resolve())
                ]
            else:
                command = [
                    "ffmpeg", "-i", str(ts_file.resolve()), "-c", "copy", "-bsf:a", "aac_adtstoasc", "-y", str(mp4_file.resolve())
                ]
            
            run(command, stdout=FFMPEG_OUTPUT_TARGET, stderr=FFMPEG_OUTPUT_TARGET, check=True)
            print(f"Converted to {mp4_file.name}")
        except CalledProcessError as e:
            print(f"FFMpeg Error on {ts_file.name}: {e}")
