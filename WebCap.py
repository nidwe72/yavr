import os, time, re, math, threading
import subprocess, signal
import random, datetime, code
from shutil import which,get_terminal_size
from typing import Union, Optional, Tuple

from rich.progress import track, TextColumn, BarColumn, TaskProgressColumn, SpinnerColumn, ProgressColumn, \
    GetTimeCallable
from rich.progress import Progress
from rich.console import Console
from rich.markdown import Markdown
from pyfiglet import Figlet
from rich.text import Text
from termcolor import colored
from rich import print as richPrint
from rich.panel import Panel
from rich.table import Table, Column

try:
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.common.keys import Keys
except:
    raise OSError('Python package selenium not found')

if which('firefox') is None:
    raise OSError('Firefox not found')

if which('Xvfb') is None:
    raise OSError('Xvfb not found')

if which('pactl') is None:
    raise OSError('pactl not found')

if which('pacmd') is None:
    raise OSError('pactl not found')

if which('ffmpeg') is None:
    raise OSError('ffmpeg not found')

def mknewfilename(filedir, filetag):
    return filedir+os.sep+filetag+'.'+datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+'.mp4'


class MyProgress(Progress):

    @classmethod
    def get_default_columns(cls) -> Tuple[ProgressColumn, ...]:
        return (
            TextColumn("[progress.description]{task.description}",table_column=Column(ratio=1)),
            BarColumn(style='black',complete_style='yellow',finished_style='green',pulse_style='yellow',table_column=Column(ratio=2),bar_width=None),
            TaskProgressColumn(style='white',markup=False,text_format="{task.percentage:>3.0f}%")
        )


    def get_renderables(self):
        yield Panel(self.make_tasks_table(self.tasks),title=None)


class WebCap:
    def __init__(self, x_res = 1280,
                       y_res = 720,
                       extent = '',
                       depth = 24,
                       framerate = 10,
                       screen = 0,
                       ffmpeg_opts = '',
                       windowed = False,
                       load = False,
                       url = "https://example.com",
                       out_file = 'output.mp4',
                       filetag = '',
                       out_dir = '',
                       duration = 0,
                       interactive = False):
        self.sink_module_id = None
        self.xvfb_process = None
        self.ffmpeg_process = None
        self.sink_mon_thread = None
        self.sink_mon_exit = True
        self.x_res = x_res
        self.y_res = y_res
        self.extent = extent
        self.depth = depth
        self.framerate = framerate
        self.ffmpeg_opts = ffmpeg_opts
        self.browser = None
        self.url = url
        self.out_file = out_file
        self.filetag = filetag
        self.out_dir = out_dir
        self.exit = False
        self.interactive = interactive
        self.duration = duration
        self.screen = screen
        self.windowed = windowed
        self.load = load
        self.start_time = None
        self.random_ids()

    def random_ids(self):
        self.display_id = random.randint(100, 999)
        self.sink_id = 'webcap'+str(self.display_id)

    def start_xvfb(self):

        with MyProgress() as progress:
            captureTask = progress.add_task("[yellow]starting virtual X frame buffer".ljust(40), total=100)

            #TODO: why 10/9 scale requried?
            pc = f"Xvfb -listen tcp :{self.display_id} -screen {self.screen} {math.ceil(self.x_res*10/9)}x{math.ceil(self.y_res*10/9)}x{self.depth}"

            self.xvfb_process = subprocess.Popen(pc, shell = True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
            time.sleep(1)
            if self.xvfb_process.returncode == None:

                table = Table(title="\nxvfb")

                table.add_column("entry")
                table.add_column("value")

                table.add_row("status", 'success')
                table.add_row("server id", str(self.display_id))

                console = Console()
                with console.capture() as capture:
                    console.print(table)
                tableText = capture.get()
                print(tableText)

                progress.update(captureTask,total=100, advance=100)
            else:
                #TODO: check if screen id currently in use
                raise SystemError('Can\'t start Xvfb')

    def create_sink(self):
        with MyProgress() as progress:

            progressTask = progress.add_task("[yellow]creating audio sink".ljust(40,' '), total=100)
            pc = f'pactl load-module module-null-sink sink_name={self.sink_id}'
            self.sink_module_id = int(subprocess.check_output(pc, shell=True).decode().strip())

            table = Table(title="\nAudio sink")

            table.add_column("entry")
            table.add_column("value")

            table.add_row("status", 'success')
            table.add_row("sink name", self.sink_id)
            table.add_row("sink module id", str(self.sink_module_id))

            console=Console()
            with console.capture() as capture:
                console.print(table)
            tableText = capture.get()
            print(tableText)

            #self.console.print(table)

            # print('sink name:', self.sink_id)
            # print('sink module id', self.sink_module_id)

            progress.update(progressTask,total=100, advance=100)
            progress.refresh()

    def start_browser(self):

        with MyProgress() as progress:
            progressTask = progress.add_task("[yellow]starting browser".ljust(40), total=100)

            os.environ["DISPLAY"] = f":{self.display_id}.{self.screen}"
            fp = webdriver.FirefoxProfile()
            fp.set_preference("permissions.default.microphone", 1)
            fp.set_preference("permissions.default.camera", 1)
            self.browser = webdriver.Firefox(firefox_profile = fp)
            self.browser.maximize_window()
            print('Browser started')
            progress.update(progressTask, total=100, advance=100)

    def before_capture(self):

        with MyProgress() as progress:
            progressTask = progress.add_task("[yellow]Loading page".ljust(40), total=100)

            if not self.load:
                print('url', self.url)
                self.browser.get(self.url)
            if not self.windowed:
                self.browser.fullscreen_window()

            progress.update(progressTask, total=100, advance=100)

    def on_capture(self):
        if self.load:
            print('Loading page#2', self.url)
            self.browser.get(self.url)

    def capture_loop(self):
        if self.interactive:
            code.interact(local={'browser':self.browser})
        else:
            self.start_time = datetime.datetime.now()
            print('Press Ctrl-C (send SIGINT) to exit, or send SIGUSR1 to creating new file. My pid is', os.getpid())

            #progress=Progress(console=self.console)

            with MyProgress() as progress:
                captureTask = progress.add_task("[yellow]capturing".ljust(40,' '), total=self.duration)

                duration = 0

                while not progress.finished or not self.exit:
                    duration += 1
                    durationPercentage = self.duration / duration

                    # print(durationPercentage)

                    time.sleep(1)

                    rnumber = str(random.randint(1, 100))

                    progress.update(captureTask, advance=1)

                    if self.duration > 0 and (datetime.datetime.now() - self.start_time).seconds > self.duration:
                        break


            # while not self.exit:
            #     time.sleep(1)
            #     duration+=1
            #     durationPercentage=self.duration/duration
            #
            #     if self.duration > 0 and (datetime.datetime.now() - self.start_time).seconds > self.duration:
            #         break

    def start_sink_changer(self):
        with MyProgress() as progress:
            progressTask = progress.add_task("[yellow]Starting audio sink changer".ljust(40, ' '), total=100)

            self.sink_mon_exit = False
            self.sink_mon_thread = threading.Thread(target=self.change_audio_sink)
            self.sink_mon_thread.start()

            progress.update(progressTask, total=100, advance=100)

    def stop_sink_changer(self):

            self.sink_mon_exit = True
            self.sink_mon_thread.join()
            print('Sink changer stopped')

    def change_audio_sink(self):


            sink_timeout = 0.1
            while not self.sink_mon_exit:

                sinks = subprocess.check_output(['pacmd', 'list-sink-inputs']).decode()
                sinks = sinks.split('\n')
                index_re = re.compile(r"\s+index:\s+([0-9]+)")
                pid_re = re.compile(r"\s+window.x11.display\s+=\s+\":([0-9]+)\.[0-9]\"")
                sink_re = re.compile(r"\s+sink:\s+[0-9]+\s+<(.*?)>")

                current_index = None
                current_display = None
                current_sink = None
                browser_sink_index = None
                for line in sinks:
                    t = index_re.match(line)
                    if t:
                        current_index = int(t.group(1))
                    t = sink_re.match(line)
                    if t:
                        current_sink = t.group(1)
                    t = pid_re.match(line)
                    if t:
                        current_display = int(t.group(1))
                        if self.display_id == current_display:
                            browser_sink_index = current_index
                            break

                if browser_sink_index != None and current_sink!=self.sink_id:
                    pc = f'pactl move-sink-input {browser_sink_index} {self.sink_id}'
                    print('Moving browser to virtual audio device:\n', pc)
                    os.system(pc)
                    sink_timeout = 1
                time.sleep(sink_timeout)


    def start_capturing(self):
        out_filename = ''
        if self.out_file == '':
            out_filename = mknewfilename(self.out_dir, self.filetag)
        else:
            out_filename = self.out_file

        print('Capturing into', out_filename)
        wsz = self.browser.get_window_size()
        print('Browser frame:', wsz)
        extent = f"{wsz['width']}x{wsz['height']}"
        offset = ""
        if self.extent != '':
            extent, offset = self.extent.split('+')
            offset = '+'+offset

        pc = f"ffmpeg -y -f x11grab -video_size {extent} -framerate {self.framerate} -draw_mouse 0 -i 127.0.0.1:{self.display_id}.{self.screen}{offset} -f pulse -i {self.sink_id}.monitor {self.ffmpeg_opts} {out_filename}"
        print('Starting capturing:\n', pc)
        self.ffmpeg_process = subprocess.Popen(pc, shell = True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,  preexec_fn=os.setsid)
        print('Capturing started.')

    def stop_capturing(self):
        os.killpg(os.getpgid(self.ffmpeg_process.pid), signal.SIGINT)
        os.waitpid(self.ffmpeg_process.pid, 0)
        print('Capturing stoped.')

    def stop_browser(self):
        self.browser.quit()
        print('Browser closed.')

    def remove_sink(self):
        os.system(f'pactl unload-module {self.sink_module_id}')
        print('Sink removed.')

    def stop_xvfb(self):
        os.killpg(os.getpgid(self.xvfb_process.pid), signal.SIGINT)
        os.waitpid(self.xvfb_process.pid, 0)
        print('xvfb stoped.')

    def start(self):

        markdown = """
## This is an h1

Rich can do a pretty *decent* job of rendering markdown.

1. This is a list item
2. This is another list item
        """

        self.console = Console()
        # md = Markdown(markdown)
        # self.console.print(md)

        # f = Figlet(font='slant')
        # f = Figlet(font='smisome1')
        #f = Figlet(font='standard')
        # f = Figlet(font='speed')
        # f = Figlet(font='5lineoblique')
        #f = Figlet(font='banner3')
        #f = Figlet(font='big')
        f = Figlet(font='block')
        #f = Figlet(font='broadway')
        #f = Figlet(font='doom')
        #f = Figlet(font='big')
        #f = Figlet(font='cyberlarge')
        # f = Figlet(font='isometric1')
        #f = Figlet(font='lean')
        #f = Figlet(font='ogre')
        #f = Figlet(font='rounded')

        #f = Figlet(font='banner3')

        #best large
        #f = Figlet(font='broadway')

        #f = Figlet(font='moscow')


        #ftext=f.renderText('Y A V R')
        #ftext = f.renderText('YAVR')

        # print(colored('----------------------------------------------------------------', 'green'))

        # ftext = f.renderText('yavr')
        # print(colored(ftext,'green'))
        #console.print(ftext,style="green")
        #console.print(colored(ftext,'green'))

        # print(colored('                   yet another video recorder', 'green'))
        #
        # print(colored('----------------------------------------------------------------', 'green'))

        text = Text(justify='center')

        # for x in ftext.split("\n"):
        #     x.center(get_terminal_size().columns-10)
        #     #print(x)
        #     text.append('\n', style="bold green")
        #     text.append(x, style="bold green")

        #text.append(*[x.center(get_terminal_size().columns) for x in f.renderText(text).split("\n")], sep="\n")
        text.append("yavr: yet another video recorder", style="bold green")
        text.append("\nversion 1.0", style="gray")
        self.console.style='white'

        panel=Panel(text,border_style='green')
        self.console.print(panel)

        self.start_xvfb()
        self.proc_sink()

    def stop(self):
        self.exit = True

    def proc_sink(self):
        self.create_sink()
        self.proc_browser()

    def proc_browser(self):
        self.start_browser()
        self.proc_page()

    def proc_page(self):
        self.start_sink_changer()
        try:
            self.before_capture()
            self.start_capturing()
            print('Capturing...')
            self.on_capture()
            self.capture_loop()
        finally:
            self.cleanUp()

    def cleanUp(self):

        with MyProgress() as progress:
            progressTask = progress.add_task("[yellow]Cleaning up".ljust(40, ' '), total=100)

            self.stop_capturing()
            progress.update(progressTask, total=100, advance=20)

            self.stop_sink_changer()
            progress.update(progressTask, total=100, advance=40)
            time.sleep(1)

            self.remove_sink()
            progress.update(progressTask, total=100, advance=60)
            time.sleep(1)

            self.stop_browser()
            progress.update(progressTask, total=100, advance=80)
            time.sleep(1)

            progress.update(progressTask, total=100, advance=100)
            self.stop_xvfb()

            progress.update(progressTask, total=100, advance=100)

