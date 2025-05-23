#!/usr/bin/env python
#
# make_movie.py:
# create QuickTime movies and GIF-animation for cytosim
#
# Copyright F. Nedelec, 2007 - 2014
#
# To make MP4 Quicktime movies, you need to install ffmpeg:
# http://www.ffmpeg.org
# via Macports: sudo port install ffmpeg
# via Brew: brew install ffmpeg
#
# To make GIF movies, you have to install:
# http://www.lcdf.org/gifsicle/
# via MacPorts: sudo port install gifsicle
# via Brew: brew install gifsicle
#
# To make PNG Quicktime movies, you need:
# http://www.3am.pair.com/QTCoffee.html
# and to encode with other codecs, you will need:
# http://www.omino.com/sw/qt_tools/
# 
#
# If you have the images already, you can directly use ffmpeg:
# ffmpeg -i imgs/image%04d.png -pix_fmt yuv420p -c:v libx264 -q:v 4 -r 10 movie.mp4
#
# Fixed bit rate:
# ffmpeg -i imgs/image%04d.png -pix_fmt yuv420p -c:v libx264 -b:v 1000k -r 10 movie.mp4
#

"""
    Create movies for cytosim in given directories

Syntax:

    make_movie.py executable-with-arguments [options] [directories]

Procedure:
    
    In each directory:
      1- call the executable to generate images
      2- invoke ffmpeg or other tools to assemble a movie
      3- delete images that were produced
    
    If images of the right kind are already present in the directory,
    you may specify an empty executable and step 1 and 3 will be skipped.

    The current directory is used if none is specified.
    If walk=1, all directories downstream of the current directory will be visited
    
Options are specified as 'option=value', without space around the '=' sign.
Existing options and their values:

    format       mp4, mov, gif       Movie file format (default = 'mp4')
    codec        mpeg4, h264         if format='mp4'   (default = 'mpeg4')
                 png, h263, h264     if format='mov'   (default = 'png')
    rate         integer             Images per second (default = 10)
    quality      integer             Quicktime: data rate (eg. 64)
                                     MPEG4: subjective quality: 1=great, 3=good
                                     GIF: number of colors (eg. 256)
    cleanup      0 or 1 (default=1)  Remove temporary images (default = 1)
    walk         0 or 1 (default=0)  Visit sub-folders recursively
    lazy         0 or 1 (default=1)  Skip files already present

Examples:

    make_movie.py 'play window_size=512,256' format=mp4 run*
    make_movie.py '~/bin/play3 zoom=2' format=mp4 run*
    make_movie.py images format=mov

History:
    Created by F. Nedelec, 14/12/2007
    Improved by Beat Rupp, March 2010
    Revised on March 19 2011 and Sept-Nov 2012 by F. Nedelec.
    F. Nedelec, 10.2013: images are created in sub-directories
    F. Nedelec, 12.2013, 9.2014: cleanup
"""

try:
    import sys, os, shutil, subprocess
except ImportError:
    print("  Error: could not load necessary python modules\n")
    sys.exit()

def executable(arg):
    return os.path.isfile(arg) and os.access(arg, os.X_OK)

# some parameters:
executable = []
source_dir = ''
format     = 'mp4'
codec      = 'png'
rate       = 13
lazy       = 1
cleanup    = True
quality    = '2'

prefix = ' make_movie.py:  '
err = sys.stderr

#------------------------------------------------------------------------

def copyFiles(files, dir):
    """
        rename files to 'image????.EXT' where '????' are consecutive numbers
    """
    cnt = 0
    res = []
    for file in files:
        [main, ext] = os.path.splitext(file)
        name = dir + '/image%04i' % cnt + ext
        if not file == name:
            shutil.copyfile(file, name)
            #err.write("    %s --> %s\n" % ( file, name ))
        res.append(name)
        cnt += 1
    return res

#------------------------------------------------------------------------

def makeImages(image_format):
    """
        call executable to generate images in sub-directory
    """
    if not executable or not os.access(executable[0], os.X_OK):
        raise IOError("no suitable executable")
    val = subprocess.call(executable + ['movie', 'image_dir='+image_dir, 'image_format='+image_format], stderr=None)
    if val:
        raise IOError("`%s' failed with value %i\n" % (executable[0], val))


def makeImagesUnzip(image_format, src='objects.cmo'):
    """
        unzip cytosim's input if necessary to make the images
    """
    tmp_file = ''
    if not os.path.isfile(src):
        tmp_file = src + '.gz'
        if os.path.isfile(tmp_file):
            cmd = "gunzip %s -c > %s" % (tmp_file, src)
            subprocess.call(cmd, shell=True)
        else:
            tmp_file = ''
    if not os.path.isfile(src):
        raise IOError("file '%s' not found!\n" % src)
    makeImages(image_format)
    if tmp_file:
        os.remove(tmp_file)


def getImages(image_format):
    """
        Get images in source directory,
        or generate them from executable
    """
    if os.path.isdir(source_dir):
        import glob
        images = glob.glob(source_dir+'/*.'+image_format);
        if images:
            err.write(prefix+"using images in folder `%s'\n" % source_dir)
            return copyFiles(images, image_dir)
        raise IOError("no suitable images found in `%s'" % source_dir)
    else:
        makeImagesUnzip(image_format)
        images = [os.path.join(image_dir, s) for s in os.listdir(image_dir)]
        if not images:
            raise IOError("could not produce images!")
        return copyFiles(images, image_dir)


def getImageSize(file):
    """
        Call ffprobe, and parse output to extract size of video
    """
    res = [256, 256];
    proc = subprocess.Popen(['ffprobe', '-v', 'quiet', '-show_streams', file], stdout=subprocess.PIPE)
    if not proc.wait():
        for line in proc.stdout:
            [key, equal, value] = line.partition('=')
            if key=="width":
                res[0] = int(value)
            elif key=="height":
                res[1] = int(value)
    return res

#------------------------------------------------------------------------

def makeMovieGIF(output):
    """
        create movie.gif in the current directory
    """
    images = getImages('gif')
    if images:
        delay = '%i' % (100/rate)
        args = [ 'gifsicle', '-O1', '--same-background', '--colors', quality, '--delay', delay ]
        args.extend(images)
        args.extend(['-o', output])
        val = subprocess.call(args)
        if val:
            raise IOError("Error: gifsicle failed with value %i\n" % val)
        return output
    return ''



def makeMovieMPEG(output):
    """
        create movie.mp4 from PNG files in the current directory using ffmpeg
    """
    images = getImages('png')
    if codec == 'h264':
        vcod = 'libx264'
    else:
        vcod = 'mpeg4'
    if images:
        args = ['ffmpeg', '-v', 'quiet', '-r', '%i'%rate, '-i', image_dir+'/image%04d.png', '-vcodec', vcod, '-q:v', quality, output]
        #print(''.join(x+' ' for x in args))
        val = subprocess.call(args) #, stdout=None,stderr=None)
        if val:
            raise IOError("Error: ffmpeg failed with value %i\n" % val)
        return output
    return ''



def makeMovieMOV(output):
    """
        create movie.mov from PNG files in the current directory
    """
    images = getImages('png')
    if images:
        args = [ 'catmovie', '-q', '-self-contained', '-o', output ]
        args.extend(images)
        val = subprocess.call(args)
        if val:
            raise IOError("Error: catmovie failed with value %i\n" % val)
        #adjust the frame-rate:
        args = [ 'modmovie', '-scaleMovieTo', '%.2f' % (len(images)/rate), output, '-save-in-place']
        val = subprocess.call(args)
        if val:
            raise IOError("Error: modmovie failed with value %i\n" % val)
        return output
    return ''


def makeMovieQT(output):
    """
    re-encode existing MOV file with QT_export,
    http://omino.com/sw/qt_tools/
    ~/bin/qt_export --audio=0 --datarate=256 --video=avc1,10,100 movie_png.mov movie.mov
    """
    if codec == 'png':
        return makeMovieMOV(output)
    mov = makeMovieMOV('movie_png.mov')
    if not os.path.isfile(mov):
        err.write(prefix+"could not make Quicktime movie\n")
        return ''
    qt_export  = '~/bin/qt_export'
    if not os.path.isfile(qt_export):
        err.write(prefix+"missing `qt_export' executable\n")
        os.rename(mov, output)
        return output
    if codec == 'h263':
        cmd = [qt_export, '--audio=0', '--datarate='+quality, '--video=h263,%i,100'%rate, mov, output]
    elif codec == 'h264':
        cmd = [qt_export, '--audio=0', '--datarate='+quality, '--video=avc1,%i,100'%rate, mov, output]
    else:
        raise IOError("codec `%s' not supported" % codec)
    subprocess.call(cmd)
    os.remove(mov)
    err.write(prefix+"created movie with datarate = %s\n" % quality)
    return output



def makeMovie(dirpath):
    """
        make movie in directory dirpath
    """
    res = 'nothing'
    if format == 'mp4':
        res = makeMovieMPEG('movie.mp4')
    elif format == 'gif':
        res = makeMovieGIF('movie.gif')
    elif format == 'mov':
        res = makeMovieQT('movie.mov')
    elif format == 'images':
        makeImagesUnzip('png')
    else:
        raise IOError("format `%s' not supported" % format)
    return res

#------------------------------------------------------------------------

def process(dirpath, directories, filenames):
    """
        make movie in directory dirpath
    """
    global image_dir, cleanup
    output = 'movie.'+format
    if ( output in filenames ) and lazy:
        err.write(prefix+"`%s/%s' already exists!\n" % (dirpath, output))
    else:
        err.write("\n")
        os.chdir(dirpath)
        err.write(prefix+"visiting `%s'\n" % dirpath)
        try:
            import tempfile
            image_dir = tempfile.mkdtemp('', 'imgs-', '.')
        except Exception as e:
            err.write(prefix+"cannot make temporary directory %s\n" % e);
        try:
            res = makeMovie(dirpath)
            err.write(prefix+"created %s\n" % res);
        except Exception as e:
            err.write(prefix+"error: %s\n" % e);
        if cleanup:
            shutil.rmtree(image_dir)
        else:
            err.write(prefix+"folder `%s' contains generated images\n" % image_dir)




def process_dir(dirpath):
    """
        call process() with appropriate arguments
    """
    files = os.listdir(dirpath)
    for f in files:
        if os.path.isdir(f):
            files.remove(f)
    process(dirpath, os.path.basename(dirpath), files)


#------------------------------------------------------------------------

def command(args):
    """
        process command line arguments
    """
    global executable, source_dir, format, cleanup, lazy, codec, rate, quality
    walk = 0
    paths = []
    
    try:
        arg = args[0]
    except:
        err.write(prefix+"you must specify an executable or a directory on the command line\n")
        sys.exit()

    arg0 = os.path.expanduser(arg.split()[0])
    if os.access(arg0, os.X_OK):
        if os.path.isdir(arg):
            source_dir = arg
        else:
            executable = arg.split();
            executable[0] = os.path.abspath(arg0)
    else:
        err.write(prefix+"You must specify an executable or a directory on the command line\n")
        sys.exit()

    for arg in args[1:]:
        [key, equal, value] = arg.partition('=')
        
        if key=='' or equal!='=' or value=='':
            if os.path.isdir(arg):
                paths.append(arg)
            else:
                err.write(prefix+"ignored '%s' on command line\n" % arg)
        else:
            if key=='rate':
                rate = int(value)
            elif key=='cleanup':
                cleanup = bool(value)
            elif key=='format':
                format = value
                if format == 'mov':
                    quality = '256'
                if format == 'gif':
                    quality = '256'
            elif key=='codec':
                codec = value
            elif key=='quality':
                quality = value
            elif key=='lazy':
                lazy = int(value)
            elif key=='walk':
                walk = int(value)
            else:
                err.write(prefix+"ignored '%s' on command line\n" % arg)

    if not paths:
        paths.append('.')

    cdir = os.getcwd()
    for path in paths:
        os.chdir(cdir)
        if walk:
            for path, dirs, files in os.walk(path, topdown=False):
                os.chdir(cdir)
                process(path, dirs, files)
        else:
            process_dir(path)



if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1]=='help':
        print(__doc__)
    else:
        command(sys.argv[1:])


