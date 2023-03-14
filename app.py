from io import StringIO
from time import sleep
from datetime import datetime
import streamlit as st
from bs4 import BeautifulSoup


def find_start_seconds(region):
    """Returns start second for region."""
    if len(region["Start"]) > 9:
        start_time = datetime.strptime(region["Start"], "%H:%M:%S.%f")
    elif len(region["Start"]) in [8, 9]:
        start_time = datetime.strptime(region["Start"], "%M:%S.%f")
    elif len(region["Start"]) < 8:
        start_time = datetime.strptime(region["Start"], "%S.%f")

    t = start_time.time()
    return (t.hour * 60 + t.minute) * 60 + t.second


def find_lenght_seconds(region):
    """Returns lenght of region in seconds."""
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
    timeline = soup.find("Tracks")
    for region in timeline.find_all("Region"):
        try:
            colors[str(region["Ref"])] = int(region["Colour"])
        except:
            pass

    soup = colorize_clipboard(soup, colors)
    soup = colorize_timeline(soup, colors)
    return soup


def colorize_clipboard(soup, colors):
    """Give colors to clips in clipboard."""

    clipboard = soup.find("Clipboard")
    for group in clipboard.find_all("Group"):
        # new_group_tag = soup.new_tag('Group', {'Caption':group['Caption'], 'IsExpanded':group['IsExpanded']})
        new_group_tag = group
        # Go over clips (nested regions).
        for clip in group.find_all("Clip"):
            # new_clip_tag = soup.new_tag('Clip', {'Name':clip['Name'], 'Start':clip['Start'], 'Length':clip['Length']})
            new_clip_tag = clip
            for region in clip.find_all("Region"):
                new_region_tag = region
                try:
                    new_region_tag["Colour"] = colors[region["Ref"]]
                except KeyError:
                    new_region_tag["Colour"] = "0"
                new_clip_tag.append(new_region_tag)
            new_group_tag.append(new_clip_tag)

        # Go over regions.
        for region in group.find_all("Region"):
            if region.parent.name == "Clip":
                continue
            new_region_tag = region
            try:
                new_region_tag["Colour"] = colors[region["Ref"]]
            except KeyError:
                new_region_tag["Colour"] = "0"
            new_group_tag.append(new_region_tag)
        new_clipboard_tag.append(new_group_tag)

    soup.Session.Clipboard.replace_with(new_clipboard_tag)

    return soup


def colorize_timeline(soup, colors):
    print(colors)
    # Give colors to clips on timeline.
    new_tracks_tag = soup.find("Tracks")
    tracks = soup.find("Tracks")

    for track in tracks.find_all("Track"):
        new_track_tag = track
        for region in track.find_all("Region"):
            new_region_tag = region
            try:
                new_region_tag["Colour"] = colors[region["Ref"]]
            except KeyError:
                print(region)
                new_region_tag["Colour"] = "0"
            new_track_tag.append(new_region_tag)
        new_tracks_tag.append(new_track_tag)
    soup.Session.Tracks.replace_with(new_tracks_tag)
    return soup


def print_analyzing(soup):
    regions = soup.find_all("Region")
    n_regions = len(regions)
    for region in regions:
        try:
            with s0:
                st.markdown(f':green[{region["Name"]}]')
                sleep(1 / (n_regions * 2))
        except KeyError:
            pass


def colorize_groups(soup):
    """Give color to regions based on groups they are in."""
    groups = soup.find_all("Group")
    ids = []
    ids_groups = []
    for group in reversed(groups):
        print(group["Caption"])
        regions = []
        # try:
        for region in group.find_all("Region"):
            if region["Ref"] not in ids:  # Exclude if already in another group.
                regions.append(region["Ref"])
        # except:
        #     pass
        ids += regions
        ids_groups.append(regions)

    colors = {}
    for group in ids_groups:
        group_color = (ids_groups.index(group) * 50) % 360
        for ref in group:
            colors[ref] = group_color

    soup = colorize_clipboard(soup, colors)
    soup = colorize_timeline(soup, colors)
    return soup


def make_rainbow(soup):
    """Returns a tracks tag colored like a rainbow."""

    new_tracks_tag = soup.find("Tracks")
    tracks = soup.find("Tracks")
    regions = tracks.find_all("Region")
    min_start = min([find_start_seconds(i) for i in regions])
    max_end = max(
        [int(find_start_seconds(i) + find_lenght_seconds(i)) for i in regions]
    )

    lenght = int(max_end - min_start)

    # Give colors to clips on timeline.
    new_tracks_tag = soup.find("Tracks")
    tracks = soup.find("Tracks")
    for track in tracks.find_all("Track"):
        new_track_tag = track
        for region in track.find_all("Region"):
            new_region_tag = region
            try:
                middle = find_start_seconds(region) + find_lenght_seconds(region) / 2
                new_region_tag["Colour"] = int(((middle) / lenght) * 360)
            except KeyError:
                new_region_tag["Colour"] = "0"
            new_track_tag.append(new_region_tag)
        new_tracks_tag.append(new_track_tag)

    soup.Session.Tracks.replace_with(new_tracks_tag)
    return soup

st.title(":green[Colorize] your :red[Hindenburg] project")

t1, t2, t3 = st.tabs(['From timeline', 'From clipboard', 'As rainbow 🌈'])
with t1:
    st.markdown(
        """
    1. Set colors for a few clips on your timeline, ideally at least one clip from
    each recording. 
    2. Upload your Hindenburg project file (ending with *.nhsx*) below to add the same color
    to other clips originating from the same recording.
    3. Choose *Colors from timeline* to download the project file **and put it in the same folder as your original project file**.  
    """
    )

    with st.expander(label="Unclear? See an example here.", expanded=False):
        st.write("*Put colors on clips like this...*")
        st.image("before.png")
        st.write("*...and you get a file that looks like this*")
        st.image("after.png")

with t2:
    st.markdown('''
    This alternative can be good if you have created clipboards for each person/interview as all clips in the same clipboard will
    be given the same color.  
    If you have clips originating from the same recording in different clipboards it will be given the
    color for the last clipbord where it is included.  
    Choose *Colors from clipboard* to download the project file **and put it in the same folder as your original project file**. 
    ''')

with t3:
    st.markdown('''
    This alternative makes your timeline into a beautiful rainbow! Lots of love but maybe not where you will start a longer project.  
    Choose *Download rainbow project!* to download the project file **and put it in the same folder as your original project file**. 
    ''')
st.markdown('No data is saved anywhere. Made by [Lasse Edfast](https://lasseedfast.se). You need to be using Hindenburg 2.0 to use colors.')
# Ask for file.
uploaded_file = st.file_uploader(
    "*Upload your project file*",
    label_visibility="hidden",
    type="nhsx",
    accept_multiple_files=False,
)

if uploaded_file:
    if "soup" not in st.session_state:  # Make soup.
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        soup = BeautifulSoup(stringio.read(), "xml")
        st.session_state["soup"] = soup
    soup = st.session_state["soup"]

    project_name = soup.find("AudioPool")["Path"].replace(" Files", "")
    new_clipboard_tag = soup.new_tag("Clipboard")

    s0 = st.empty()
    with s0:
        if 'analyzed' not in st.session_state:
            print_analyzing(soup)
            sleep(1)
            
        st.session_state['analyzed'] = True
        st.markdown("Choose your colors:")
        sleep(0.3)
    # Area to print things.
    c1, c2, c3 = st.columns(3)

    with c1:
        if "soup1" not in st.session_state:
            soup1 = colorize(soup)
            st.session_state["soup1"] = soup1
        soup1 = st.session_state["soup1"]

        # Allow the user to download file.
        st.download_button(
            "🎨 Colors from timeline",
            soup1.encode("utf-8"),
            file_name=f"{project_name}_colors.nhsx",
        )

    with c2:
        if "soup2" not in st.session_state:
            soup2 = colorize_groups(soup)
            st.session_state["soup2"] = soup2
        soup2 = st.session_state["soup2"]
        st.download_button(
            "🎨 Colors from clipboard",
            soup2.encode("utf-8"),
            file_name=f"{project_name}_colors.nhsx",
        )
    with c3:
        if "soup3" not in st.session_state:
            soup3 = make_rainbow(soup)
            st.session_state["soup3"] = soup3
        else:
            soup3 = st.session_state["soup3"]
        
        s3 = st.empty()
        with s3:
            rainbow = st.button("🌈 Rainbow timeline!")
        
        if rainbow:
            for _ in range(0, 4):
                with s3:
                    st.markdown("🌧️")
                    sleep(0.4)
                with s3:
                    st.markdown("")
                    sleep(0.15)
            with s3:
                st.markdown("🌦️")
                sleep(1)
            with s3:
                rainbows = []
                for _ in range(0, 10):
                    rainbows.append("🌈")
                    st.markdown("".join(rainbows))
                    sleep(0.09)

            with s3:
                st.download_button(
                    "🌈 Download rainbow project! 🌈",
                    soup3.encode("utf-8"),
                    file_name=f"{project_name}_rainbow.nhsx",
                )
