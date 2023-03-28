import os
from datetime import timedelta, datetime, date

import click
import cv2
import pysrt
from rich import box
from rich.console import Console
from rich.table import Table

console = Console()

VIDEO_EXTENSIONS = ('.mp4',)
SUBTITLES_EXTENSIONS = ('.srt',)
END_TIME_DEVIATION = 2


@click.command()
@click.argument('video_path')
@click.argument('subtitles_path', nargs=-1, type=click.Path(exists=True))
def matching(video_path, subtitles_path):
    if not subtitles_path:
        subtitles_path = video_path

    video_files = list()
    subtitle_files = list()
    subtitles = dict()
    videos = dict()

    for filename in os.listdir(video_path):
        if os.path.splitext(filename)[1] in VIDEO_EXTENSIONS:
            filepath = os.path.join(video_path, filename)
            video_files.append(filepath)
            # console.log(f"Found video file: {filepath}")

    for filename in os.listdir(subtitles_path):
        if os.path.splitext(filename)[1] in SUBTITLES_EXTENSIONS:
            filepath = os.path.join(video_path, filename)
            subtitle_files.append(filepath)
            # console.log(f"Found subtitles file: {filepath}")

    for subtitle_file in subtitle_files:
        subs = parse_subtitles(subtitle_file)
        subtitles[subtitle_file] = {
            'subtitles': subs,
            'duration': get_subtitles_duration(subs)
        }

    for video_file in video_files:
        videos[video_file] = {
            'duration': get_duration(video_file),
        }

        for subtitles_item in subtitles.items():
            if int(abs(videos[video_file]['duration'] - subtitles_item[1]['duration'])) < END_TIME_DEVIATION:
                videos[video_file]['srt'] = os.path.basename(subtitles_item[0])
                videos[video_file]['subtitles_duration'] = subtitles_item[1]['duration']

    table = Table(
        show_header=True,
        title="Соответствие субтитров", title_style='bold dark_orange',
        caption=f'Путь к видео: {video_path} \nПуть к субтитрам: {subtitles_path}',
        caption_justify='left', header_style="bold dark_orange",
        box=box.SQUARE_DOUBLE_HEAD, row_styles=["", "dim"]
    )
    table.add_column("Видео", ratio=4)
    table.add_column("Файл субтитров", ratio=4)
    table.add_column("Длительность видео", justify="right", style="blue", ratio=2)
    table.add_column("Длительность субтитров", justify="left", style="blue", ratio=2)
    for video in videos.items():
        table.add_row(
            os.path.basename(video[0]),
            str(video[1].get('srt', '')),
            str(video[1]['duration']),
            str(video[1].get('subtitles_duration', '-')),
        )

    console.print(table)


def get_subtitles_duration(subtitles: list) -> float:
    duration = datetime.combine(date.min, subtitles[-1].end.to_time()) - datetime.min
    return duration.total_seconds()


def parse_subtitles(subtitle_file):
    return pysrt.open(subtitle_file)


def get_duration(filename):
    video = cv2.VideoCapture(filename)

    fps = video.get(cv2.CAP_PROP_FPS)  # OpenCV v2.x used "CV_CAP_PROP_FPS"
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    int_seconds = int(frame_count / fps)
    return timedelta(seconds=int_seconds).total_seconds()


def get_frame_count(filename):
    video = cv2.VideoCapture(filename)
    return video.get(cv2.CAP_PROP_FRAME_COUNT)


if __name__ == '__main__':
    matching()
