from io import StringIO
from time import sleep
from datetime import datetime
import streamlit as st
from bs4 import BeautifulSoup


def find_start_seconds(region):
    ''' Returns start second for region. '''
    if len(region["Start"]) > 9:
        start_time = datetime.strptime(region["Start"], "%H:%M:%S.%f")
    elif len(region["Start"]) in [8, 9]:
        start_time = datetime.strptime(region["Start"], "%M:%S.%f")
    elif len(region["Start"]) < 8:
        start_time = datetime.strptime(region["Start"], "%S.%f")

    t = start_time.time()
    return (t.hour * 60 + t.minute) * 60 + t.second

def find_lenght_seconds(region):
    ''' Returns lenght of region in seconds. '''
    if len(region["Length"]) > 9:
        lenght = datetime.strptime(region["Length"], "%H:%M:%S.%f")
    elif len(region["Length"]) in [8, 9]:
        lenght = datetime.strptime(region["Length"], "%M:%S.%f")
    elif len(region["Length"]) < 8:
        lenght = datetime.strptime(region["Length"], "%S.%f")
    t = lenght.time()
    return (t.hour * 60 + t.minute) * 60 + t.second

def colorize(soup):
    # Get colors from clips on timeline.
    colors = {}
    n_regions = len(timline.find_all("Region"))
    for region in timline.find_all("Region"):
        try:
            colors[str(region["Ref"])] = int(region["Colour"])
        except:
            pass

    # Give colors to clips in clipboard
    for group in soup.find_all("Group"):
        new_group_tag = group
        for region in group.find_all("Region"):
            try:
                with s:
                    st.markdown(f':green[{region["Name"]}]')
                    sleep(1/(n_regions/3))
            except KeyError:
                pass
            new_region_tag = region
            try:
                new_region_tag["Colour"] = colors[region["Ref"]]
            except KeyError:
                new_region_tag["Colour"] = "0"
            new_group_tag.append(new_region_tag)
        new_clipboard_tag.append(new_group_tag)

    soup.Session.Clipboard.replace_with(new_clipboard_tag)

    # Give colors to clips on timeline.
    new_tracks_tag = soup.find("Tracks")
    tracks = soup.find("Tracks")
    for track in tracks.find_all("Track"):
        try:
            with s:
                st.markdown(f':green[{region["Name"]}]')
                sleep(1/(n_regions/3))
        except KeyError:
            pass
        new_track_tag = track
        for region in track.find_all("Region"):
            new_region_tag = region
            try:
                new_region_tag["Colour"] = colors[region["Ref"]]
            except KeyError:
                new_region_tag["Colour"] = "0"
            new_track_tag.append(new_region_tag)
        new_tracks_tag.append(new_track_tag)
    soup.Session.Tracks.replace_with(new_tracks_tag)
    return soup

def make_rainbow(soup):
    ''' Returns a tracks tag colored like a rainbow. '''

    new_tracks_tag = soup.find("Tracks")
    tracks = soup.find("Tracks")
    regions = tracks.find_all("Region")
    min_start = min([find_start_seconds(i) for i in regions])
    max_end = max([int(find_start_seconds(i) + find_lenght_seconds(i)) for i in regions])

    lenght = int(max_end-min_start)

    # Give colors to clips on timeline.
    new_tracks_tag = soup.find("Tracks")
    tracks = soup.find("Tracks")
    for track in tracks.find_all("Track"):
        new_track_tag = track
        for region in track.find_all("Region"):
            new_region_tag = region
            try:
                middle = find_start_seconds(region) + find_lenght_seconds(region)/2
                new_region_tag["Colour"] = int(((middle)/lenght)*360)
            except KeyError:
                new_region_tag["Colour"] = "0"
            new_track_tag.append(new_region_tag)
        new_tracks_tag.append(new_track_tag)

    return new_tracks_tag

print_sleep = False

st.title(":green[Colorize] your :red[Hindenburg] project")

st.markdown(
    """
1. Set colors for a few clips on your timeline, ideally at least one clip from
each recording. 
2. Upload your Hindenburg project file (ending with *.nhsx*) below to add the same color
to other clips originating from the same recording.
3. Download the modified file *and put it in the same folder as your original project file*.  
**No data is saved anywhere**. Made by [Lasse Edfast](https://lasseedfast.se). You need to be using Hindenburg 2.0 to use colors. 
"""
)

with st.expander(label='Unclear? See an example here.', expanded=False):
    st.write('*Put colors on clips like this...*')
    st.image('before.png')
    st.write('*...and you get a file that looks like this*')
    st.image('after.png')

# Ask for file.
uploaded_file = st.file_uploader(
    "*Upload your project file*", label_visibility="hidden", type="nhsx", accept_multiple_files=False
)

if uploaded_file:
    # Make soup.
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    soup = BeautifulSoup(stringio.read(), "xml")

    project_name = soup.find("AudioPool")["Path"].replace(" Files", "")
    new_clipboard_tag = soup.new_tag("Clipboard")

    timline = soup.find("Tracks")

    # Area to print things.
    c1, c2 = st.columns(2)
    with c1:
        s = st.empty()

    if 'soup' not in st.session_state:
        soup = colorize(soup)
        st.session_state['soup'] = soup
        print_sleep = True # Sleep while with print if first run.
    else:
        soup = st.session_state['soup']

    # Allow the user to download file.
        
    with c1:
        with s:
            if print_sleep:
                st.markdown(":green[Exporting...]")
                sleep(0.7)
            st.download_button(
                "🎈 Download file",
                soup.encode("utf-8"),
                file_name=f"{project_name}_colors.nhsx",
            )

    with c2:
        e = st.empty()
        with e:
            rainbow = st.button('🌈 Turn timeline into a rainbow! 🌈')
        if rainbow:
            for _ in range(0, 4):
                with e:
                    st.markdown('🌧️')
                    sleep(0.4)
                with e:
                    st.markdown('')
                    sleep(0.15)
            with e:
                st.markdown('🌦️')
                sleep(1)
            with e:
                rainbows = []
                for _ in range(0,10):
                    rainbows.append('🌈')
                    st.markdown(''.join(rainbows))
                    sleep(0.09)
            new_tracks_tag = make_rainbow(soup)
            soup.Session.Tracks.replace_with(new_tracks_tag)
            with e:
                st.download_button(
                "🌈 Download rainbow project",
                soup.encode("utf-8"),
                file_name=f"{project_name}_rainbow.nhsx",
            )
