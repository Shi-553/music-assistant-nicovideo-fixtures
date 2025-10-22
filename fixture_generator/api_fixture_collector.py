"""Fixture data collection handlers for different categories."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fixture_data.shared_types import StreamFixtureData
from fixture_generator.constants import (
    SAMPLE_MYLIST_ID,
    SAMPLE_SERIES_ID,
    SAMPLE_USER_ID,
    SAMPLE_VIDEO_ID,
)

if TYPE_CHECKING:
    from niconico import NicoNico

    from fixture_generator.types import FixtureProcessorProtocol

logger = logging.getLogger(__name__)


class APIFixtureCollector:
    """Collects fixture data by calling APIs for different categories."""

    def __init__(
        self,
        fixture_processor: FixtureProcessorProtocol,
        client: NicoNico,
        limit: int = 1,
    ) -> None:
        """Initialize with fixture saver dependency and data limit for API responses."""
        self.fixture_processor = fixture_processor
        self.client = client
        self.limit = limit

    async def collect_tracks_fixtures(
        self,
    ) -> None:
        """Collect TRACKS category fixtures."""
        logger.info("=== Collecting TRACKS fixtures ===")

        # Own videos
        await self.fixture_processor.process_fixture(
            "tracks",
            "own_videos",
            self.client.user.get_own_videos,
        )

        # Individual video retrieval (watch data - used as track details in provider)
        await self.fixture_processor.process_fixture(
            "tracks",
            "watch_data",
            self.client.video.watch.get_watch_data,
            SAMPLE_VIDEO_ID,
        )

        # User video list (specific user's uploaded videos - converts to Track objects)
        await self.fixture_processor.process_fixture(
            "tracks",
            "user_videos",
            self.client.user.get_user_videos,
            str(SAMPLE_USER_ID),
            page=1,
            page_size=self.limit,
        )

    async def collect_playlists_fixtures(
        self,
    ) -> None:
        """Collect PLAYLISTS category fixtures."""
        logger.info("=== Collecting PLAYLISTS fixtures ===")

        # Own mylists (used as library playlists in provider)
        await self.fixture_processor.process_fixture(
            "playlists",
            "own_mylists",
            self.client.user.get_own_mylists,
        )

        # Following mylists (used as following playlists in provider)
        await self.fixture_processor.process_fixture(
            "playlists",
            "following_mylists",
            self.client.user.get_own_following_mylists,
        )

        # Individual mylist retrieval
        await self.fixture_processor.process_fixture(
            "playlists",
            "single_mylist_details",
            self.client.video.get_mylist,
            str(SAMPLE_MYLIST_ID),
            page_size=self.limit,
            page=1,
        )

    async def collect_albums_fixtures(
        self,
    ) -> None:
        """Collect ALBUMS category fixtures."""
        logger.info("=== Collecting ALBUMS fixtures ===")

        # Own series (used as library albums in provider)
        await self.fixture_processor.process_fixture(
            "albums",
            "own_series",
            self.client.user.get_own_series,
        )

        # User series list (converts to Album objects)
        await self.fixture_processor.process_fixture(
            "albums",
            "user_series",
            self.client.user.get_user_series,
            str(SAMPLE_USER_ID),
            page=1,
            page_size=self.limit,
        )

        # Individual series retrieval
        await self.fixture_processor.process_fixture(
            "albums",
            "single_series_details",
            self.client.video.get_series,
            str(SAMPLE_SERIES_ID),
            page=1,
            page_size=self.limit,
        )

    async def collect_artists_fixtures(
        self,
    ) -> None:
        """Collect ARTISTS category fixtures."""
        logger.info("=== Collecting ARTISTS fixtures ===")

        # Following users (used as library artists in provider)
        await self.fixture_processor.process_fixture(
            "artists", "following_users", self.client.user.get_own_followings, page_size=self.limit
        )

        # Test user
        await self.fixture_processor.process_fixture(
            "artists",
            "user_details",
            self.client.user.get_user,
            str(SAMPLE_USER_ID),
        )

    async def collect_search_fixtures(
        self,
    ) -> None:
        """Collect SEARCH category fixtures."""
        logger.info("=== Collecting SEARCH fixtures ===")

        # Video search
        await self.fixture_processor.process_fixture(
            "search",
            "video_search_keyword",
            self.client.video.search.search_videos_by_keyword,
            "APIテスト68461151-45285955",
            sort_key="registeredAt",
            sort_order="asc",
            page_size=self.limit,
        )

        # Tag search
        await self.fixture_processor.process_fixture(
            "search",
            "video_search_tags",
            self.client.video.search.search_videos_by_tag,
            "APIテストタグ68461151-45285955",
            sort_key="registeredAt",
            sort_order="asc",
            page_size=self.limit,
        )

        # Mylist search
        await self.fixture_processor.process_fixture(
            "search",
            "mylist_search",
            self.client.video.search.search_lists,
            "テストマイリスト68461151-78597499",
            sort_key="startTime",
            sort_order="asc",
            page_size=self.limit,
            types=["mylist"],
        )

        # Series search
        await self.fixture_processor.process_fixture(
            "search",
            "series_search",
            self.client.video.search.search_lists,
            "テストシリーズ68461151-527007",
            sort_key="startTime",
            sort_order="asc",
            page_size=self.limit,
            types=["series"],
        )

    async def collect_history_fixtures(
        self,
    ) -> None:
        """Collect HISTORY category fixtures."""
        logger.info("=== Collecting HISTORY fixtures ===")

        # History
        await self.fixture_processor.process_fixture(
            "history",
            "user_history",
            self.client.video.get_history,
            page_size=self.limit,
        )

        # Like history
        await self.fixture_processor.process_fixture(
            "history",
            "user_likes",
            self.client.video.get_like_history,
            page_size=self.limit,
        )

    async def collect_stream_fixtures(
        self,
    ) -> None:
        """Collect STREAM category fixtures."""
        logger.info("=== Collecting STREAM fixtures ===")

        # Get watch data
        watch_data_result = self.client.video.watch.get_watch_data(SAMPLE_VIDEO_ID)

        # Select best audio (same logic as server-side _select_best_audio)
        best_audio = None
        best_quality = -1
        for audio in watch_data_result.media.domand.audios:
            if audio.is_available and audio.quality_level > best_quality:
                best_audio = audio
                best_quality = audio.quality_level

        if not best_audio:
            logger.warning("No available audio found for stream fixture")
            return

        # Create StreamFixtureData structure
        stream_fixture = StreamFixtureData(
            watch_data=watch_data_result,
            selected_audio=best_audio,
        )

        # Save as fixture
        await self.fixture_processor.process_fixture(
            "stream",
            "stream_data",
            lambda: stream_fixture,  # Return the constructed StreamFixtureData
        )

    async def collect_all_fixtures(
        self,
    ) -> None:
        """Collect all fixtures using the provided client."""
        logger.info("Starting fixture collection...")

        # Collect fixtures for each category
        await self.collect_tracks_fixtures()
        await self.collect_playlists_fixtures()
        await self.collect_albums_fixtures()
        await self.collect_artists_fixtures()
        await self.collect_search_fixtures()
        await self.collect_history_fixtures()
        await self.collect_stream_fixtures()

        logger.info("=== All fixtures collected successfully! ===")
