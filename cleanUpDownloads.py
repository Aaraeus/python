# A torrent cleaner running on Windows. Give it a folder name and it renames files for you.

# ----- INFORMATION -----
__author__ = "Aaraeus"
__copyright__ = "None"
__credits__ = ["Aaraeus", "TMDB API", "TVDB API", "Parse Torrent Name"]
__license__ = "N/A"
__version__ = "2.0.0"
__maintainer__ = "Aaraeus"
__email__ = "Message_me_on_GITHUB"
__status__ = "Production"

# ----- VERSION CONTROL -----
# v1. Created
#
# v2. Added the following features:
#
#       a.  You need to add an exception handler if the title of the episode returned from TVDB
#           has a special character, e.g. Futurama S07E16.
#           Futurama.S07E16.T.The.Terrestrial.720p.WEB-DL.x264.AAC
#           This returns T.: The Terrestrial from TVDB.
#
#       b.  Make the code recognise if it's a movie. This won't have a season or episode number.

# ----- MODULES -----
import os
import re
import PTN
import tmdbsimple as tmdb
import tvdb_api
from operator import itemgetter
import datetime

# ----- Get secrets like API keys -----
import secrets

# ----- USER INPUTS -----
# User input - filepath. Use double slashes for Windows paths.
filePathInput = r'C:\Users\Kintesh\Videos\TV Shows\Futurama - Seasons 1-7\Futurama - Season 2'

# Name Cleaner function - gets the file name and returns the new string, and a boolean 1/0 value of whether
# the right amount of information was found in the existing string. This is used to determine whether the file
# should actually be renamed.

# Here's a test name in case I need to do some debugging later.
#testName = 'The.Big.Bang.Theory.S07E01.HDTV.x264-LOL.mp4'
#testName = 'Jason Bourne' # (Prefix with 'Jesus Christ')
#testName = 'Futurama.S07E16.T.The.Terrestrial.720p.WEB-DL.x264.AAC.mp4'

def CleanThis(torrentString):
    # This is the important bit - use Parse Torrent Name to extract information.
    # Note - I use mydict.get() rather than mydict['key'] because I want a None value
    # passed to the variable if it's not found.
    # If we can find season/episode numbers, we have a tv show. otherwise, it is a movie.

    info = PTN.parse(torrentString)
    title = info.get('title')

    # Clean up for US and UK tv shows - change this if required.
    if title.lower() == 'the big bang theory':
        title = 'The Big Bang Theory'

    # Clean up the season and episode numbers a little to be in S01E01 format.
    s = info.get('season')
    e = info.get('episode')

    if not s:
        pass # Do nothing if the string is empty.
    elif s < 10:
        season = '0' + str(s)
    else:
        season = str(s)

    if not e:
        pass # Do nothing if the string is empty.
    elif e < 10:
        episode = '0' + str(e)
    else:
        episode = str(e)

    # Get the container (also known as the file extension). This is pretty much critical to know.
    container = info.get('container')

    # Now use the TVDB API to get the TV show episode name from, well, TVDB.

    # If either s or e is empty, classify this as a movie. Otherwise classify it as a tv show.
    if not s or not e:
        classification = 'movie'
    else:
        classification = 'tv_show'

    # DEALING WITH A TV SHOW. Search TVDB. If it isn't there, return an error.

    if classification == 'tv_show':
        t = tvdb_api.Tvdb()
        episodeInfo = t[title][s][e]  # get season s, episode e of show
        rawEpisodeName = episodeInfo.get('episodename')

        # Regular Expression to remove special characters from name.
        episodeName = re.sub('[^[^\w\-_ ]', '', rawEpisodeName)

        # Finally, do an error check. If any of the above inputs are null, then return a null string.
        if not title:
            newString = None
        elif not s:
            newString = None
        elif not e:
            newString = None
        elif not episodeName:
            newString = None
        elif not container:
            newString = None
        else:
            # Print some stuff out to the console, because, y'know, debugging and all that.
            print('Information extracted: ')
            print('Classification: ' + classification)
            print('Title is: ' + title)
            print('Season and Episode: S' + str(season) + 'E' + str(episode))
            print('Container: ' + container)
            print('Episode name is: ' + episodeName)  # Print episode name
            print('')

            newString = title + ' - ' 'S' + str(season) + 'E' + str(episode) + ' - ' + episodeName + '.' + container

        return newString

    elif classification == 'movie':
        # Search the Movie Database for the title in question.
        search = tmdb.Search()
        response = search.movie(query=title)

        # How many results did we find?
        results = response['total_results']

        # If we find 0 results, return a null string.
        if results == 0:
            newString = None
        else:
            # Sort search results by descending popularity.
            search_results = sorted(search.results, key=itemgetter('popularity'), reverse=True)

            # Find most popular result.
            most_popular = search_results[0]

            tvdb_raw_title = most_popular['title']
            tvdb_id = most_popular['id']
            tvdb_release_dt = most_popular['release_date']

            # Regular Expression to remove special characters from name.
            tvdb_title = re.sub('[^[^\w\-_ ]', '', tvdb_raw_title)

            tvdb_release_year = datetime.datetime.strptime(tvdb_release_dt, "%Y-%m-%d").year

            # Finally, do an error check. If any of the above inputs are null, then return a null string.
            if not title:
                newString = None
            elif not tvdb_title:
                newString = None
            elif not tvdb_id:
                newString = None
            elif not container:
                newString = None
            else:
                # Print some stuff out to the console, because, y'know, debugging and all that.
                print('Information extracted: ')
                print('Classification: ' + classification)
                print('Title is: ' + title)
                print('Container: ' + container)
                print('TVDB title: ' + tvdb_title)
                print('TVDB ID: ' + str(tvdb_id))
                print('TVDB Release Date: ' + tvdb_release_dt)
                print('TVDB Release Year: ' + str(tvdb_release_year))
                print('')
                newString = tvdb_title +  ' - ' + str(tvdb_release_year) + '.' + container

        return newString

# ----- TEST EXECUTION SEGMENT - FOR EDITING AND ENHANCING THE MAIN FUNCTION ONLY! -----
# if not CleanThis(testName):
#     print('Error - shouldn\'t rename this file!')
# else:
#     print('Original String is: ' + testName)
#     print('Final Result is: ' + CleanThis(testName))


# ----- LOOP THROUGH DIRECTORY AND RENAME -----
# Loop through a designated filePathInput (and all subfolders)!

for folderName, subfolders, filenames in os.walk(filePathInput):
    print('The current folder is ' + folderName)

    for subfolder in subfolders:
        print('SUBFOLDER OF ' + folderName + ': ' + subfolder)

    for filename in filenames:
        try:
            print('FILE INSIDE ' + folderName + '\\' + filename)
            print('RENAMING TO: ' + folderName + '\\' + CleanThis(filename))
            print('')
            # Actual renaming is done next. NOTE THAT THIS DOES NOT ACCOUNT FOR ERRORS.
            # WHAT HAPPENS WHEN NAMECLEANER RETURNS A NONETYPE?!?!!!!
            os.rename(folderName + '\\' + filename, folderName + '\\' + CleanThis(filename))
        except TypeError:
            print('ERROR: ' + filename + ' file not renamed.')
        except OSError:
            print('ERROR: ' + filename + ' was not renamed because it contains special characters, probably.')
