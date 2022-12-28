from WebCap import WebCap


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    #parser.add_argument('-p', "--profile", default='default', help="Web application profile to capture: "+str(list(profiles.keys())))
    parser.add_argument('-P', "--mode", default='', help="Mode for profile")
    parser.add_argument('-x', "--xres", type=int, default=1280, help="Virtual screen X, default 1280")
    parser.add_argument('-y', "--yres", type=int, default=720, help="Virtual screen Y, default 740")
    parser.add_argument('-e', "--depth", type=int, default=24, help="Virtual screen color depth, default 24")
    parser.add_argument('-t', "--extent", default='', help="Capturing extent ex. 400x500+100,100, default as screen")
    parser.add_argument('-s', "--screen", type=int, default=0, help="Virtual screen number, default 0")
    parser.add_argument('-f', "--framerate", type=int, default=10, help="Capture frame rate, default 10")
    parser.add_argument('-i', "--interactive", action='store_true', default=False, help="Run interactive python console with browser object after starting capturing")
    parser.add_argument('-m', "--ffmpeg", type=str, default='', help="Additional ffmpeg arguments")
    parser.add_argument('-o', "--output", default='', help="Output file")
    parser.add_argument('-O', "--outputdir", default='', help="Output directory")
    parser.add_argument('-g', "--filetag", default='webcap', help="Output file")
    parser.add_argument('-w', "--windowed", action='store_true', default=False, help="Do not turn browser into fullscreen mode")
    parser.add_argument('-u', "--url", required=False, help="Target url")
    parser.add_argument('-l', "--load", action='store_true', default=False, help="Loading page after capturing started")
    parser.add_argument('-d', "--duration", type=int, default=0, help="Capture duration in sec, default no limit")

    args = parser.parse_args()

    webCap = WebCap(duration=10)

    # cap_object = profiles[args.profile](x_res = args.xres,
    #                                     y_res = args.yres,
    #                                     extent = args.extent,
    #                                     depth = args.depth,
    #                                     framerate = args.framerate,
    #                                     screen = args.screen,
    #                                     ffmpeg_opts = args.ffmpeg,
    #                                     windowed = args.windowed,
    #                                     load = args.load,
    #                                     url = args.url,
    #                                     out_file = args.output,
    #                                     filetag = args.filetag,
    #                                     out_dir = args.outputdir,
    #                                     duration = args.duration,
    #                                     interactive = args.interactive)

    #cap_object.set_mode(args.mode)

    #install_hooks(cap_object)

    webCap.start()