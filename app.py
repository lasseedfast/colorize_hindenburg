from io import StringIO
from time import sleep

import streamlit as st
from bs4 import BeautifulSoup

st.title("Colorize your Hindenburg project")

st.markdown(
    """
- Set colors for a few clips on your timeline, ideally at least one clip from
each recording. 
- Upload your Hindenburg project file (ending with *nhsx*) to add the same color
to other clips originating from the same recording.
- Download the modified file *and put it in the same folder as your original project file*.
"""
)

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

    # Get colors from clips on timeline.
    colors = {}
    timline = soup.find("Tracks")
    n_regions = len(timline.find_all("Region"))
    for region in timline.find_all("Region"):
        try:
            colors[str(region["Ref"])] = int(region["Colour"])
        except:
            pass
    
    # Area to print things.
    s = st.empty()

    # Give colors to clips in clipboard
    for group in soup.find_all("Group"):
        new_group_tag = group
        for region in group.find_all("Region"):
            try:
                s.markdown(f':green[{region["Name"]}]')
                sleep(1/n_regions)
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
            s.markdown(f':green[{region["Name"]}]')
            sleep(1/n_regions)
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

    # Allow the user to download file.
    with s:
        st.markdown(":green[Exporting...]")
        sleep(0.7)
        st.download_button(
            "Download file",
            soup.encode("utf-8"),
            file_name=f"{project_name}_colors.nhsx",
        )
