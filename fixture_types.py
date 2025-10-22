"""Fixture type mappings for automatic deserialization."""

from __future__ import annotations

from typing import TYPE_CHECKING

from niconico.objects.user import UserSeriesItem
from niconico.objects.nvapi import RelationshipUsersData
from music_assistant.providers.nicovideo.converters.stream import StreamConversionData
from niconico.objects.nvapi import ListSearchData
from niconico.objects.nvapi import SeriesData
from niconico.objects.nvapi import OwnVideosData
from niconico.objects.nvapi import UserVideosData
from niconico.objects.user import NicoUser
from niconico.objects.nvapi import VideoSearchData
from niconico.objects.nvapi import LikeHistoryData
from niconico.objects.video import Mylist
from niconico.objects.nvapi import HistoryData
from niconico.objects.nvapi import FollowingMylistsData
from niconico.objects.video.watch import WatchData
from niconico.objects.user import UserMylistItem

if TYPE_CHECKING:
    from pydantic import BaseModel

# Fixture type mappings: path -> type
FIXTURE_TYPE_MAPPINGS: dict[str, type[BaseModel]] = {
    "tracks/own_videos.json": OwnVideosData,
    "tracks/watch_data.json": WatchData,
    "tracks/user_videos.json": UserVideosData,
    "playlists/own_mylists.json": UserMylistItem,
    "playlists/following_mylists.json": FollowingMylistsData,
    "playlists/single_mylist_details.json": Mylist,
    "albums/own_series.json": UserSeriesItem,
    "albums/user_series.json": UserSeriesItem,
    "albums/single_series_details.json": SeriesData,
    "artists/following_users.json": RelationshipUsersData,
    "artists/user_details.json": NicoUser,
    "search/video_search_keyword.json": VideoSearchData,
    "search/video_search_tags.json": VideoSearchData,
    "search/mylist_search.json": ListSearchData,
    "search/series_search.json": ListSearchData,
    "history/user_history.json": HistoryData,
    "history/user_likes.json": LikeHistoryData,
    "stream/stream_data.json": StreamConversionData,
}
