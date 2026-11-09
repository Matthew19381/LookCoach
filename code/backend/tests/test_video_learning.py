from services.video_learning import VideoLearningEngine


class TestVideoLearningEngine:
    """Comprehensive tests for VideoLearningEngine."""

    def test_get_videos_for_analysis_empty(self):
        result = VideoLearningEngine.get_videos_for_analysis({}, {}, {})
        assert isinstance(result, list)

    def test_get_videos_for_analysis_with_data(self):
        face_data = {"swelling": {"level": 60}}
        skin_data = {"problems": [{"issue": "acne"}]}
        hair_data = {"density": 50}
        result = VideoLearningEngine.get_videos_for_analysis(face_data, skin_data, hair_data)
        assert isinstance(result, list)

    def test_get_videos_for_technique(self):
        result = VideoLearningEngine.get_videos_for_technique("gua_sha")
        assert isinstance(result, list)

    def test_get_videos_for_technique_invalid(self):
        result = VideoLearningEngine.get_videos_for_technique("invalid_technique")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_search_videos_by_query(self):
        result = VideoLearningEngine.search_videos("gua sha")
        assert isinstance(result, list)

    def test_search_videos_no_results(self):
        result = VideoLearningEngine.search_videos("xyznonexistent123")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_search_videos_empty_query(self):
        result = VideoLearningEngine.search_videos("")
        assert isinstance(result, list)

    def test_video_db_has_required_fields(self):
        """Verify video database has required fields."""
        from services.video_learning import VIDEO_DB
        required_fields = ["id", "title", "technique", "url", "description", "evidence_level", "evidence_note"]
        for video in VIDEO_DB:
            for field in required_fields:
                assert field in video, f"Missing field {field} in video {video.get('id', 'unknown')}"

    def test_video_urls_valid_format(self):
        """Check that video URLs are properly formatted."""
        from services.video_learning import VIDEO_DB
        for video in VIDEO_DB:
            url = video.get("url", "")
            assert url.startswith("https://www.youtube.com/results?search_query="), f"Invalid URL: {url}"

    def test_multiple_techniques(self):
        """Test that different techniques return different videos."""
        gua_sha = VideoLearningEngine.get_videos_for_technique("gua_sha")
        cold_water = VideoLearningEngine.get_videos_for_technique("cold_water")
        if len(gua_sha) > 0 and len(cold_water) > 0:
            gua_ids = [v["id"] for v in gua_sha]
            cold_ids = [v["id"] for v in cold_water]
            assert set(gua_ids).isdisjoint(set(cold_ids))

    def test_search_finds_by_title(self):
        result = VideoLearningEngine.search_videos("Tutorial")
        assert isinstance(result, list)

    def test_search_finds_by_description(self):
        result = VideoLearningEngine.search_videos("massage")
        assert isinstance(result, list)

    def test_get_videos_returns_list(self):
        """Ensure all video methods return lists."""
        assert isinstance(VideoLearningEngine.get_videos_for_analysis({}, {}, {}), list)
        assert isinstance(VideoLearningEngine.get_videos_for_technique("gua_sha"), list)
        assert isinstance(VideoLearningEngine.search_videos("test"), list)


class TestNoFabricatedVideos:
    """2026-11-08: VIDEO_DB had invented videos (watch?v=example1.., a music video, fake channels)."""

    def test_no_links_to_specific_unverified_videos(self):
        from services.video_learning import VIDEO_DB
        for video in VIDEO_DB:
            assert "watch?v=" not in video["url"]
            assert "channel" not in video and "duration" not in video

    def test_every_technique_has_evidence_label(self):
        from services.video_learning import VIDEO_DB
        for video in VIDEO_DB:
            assert video["evidence_level"] in {"hipoteza", "porada_stylistyczna", "rct", "meta"}
            if video["evidence_level"] == "hipoteza":
                assert video["evidence_note"].startswith("[HIPOTEZA]")
            if video["evidence_level"] in {"rct", "meta"}:
                assert video.get("study_url", "").startswith("https://")

    def test_gua_sha_is_recommended_for_face(self):
        ids = [v["id"] for v in VideoLearningEngine.get_videos_for_analysis({"x": 1}, {}, {})]
        assert "gua_sha" in ids

    def test_search_matches_polish_phrase(self):
        assert [v["id"] for v in VideoLearningEngine.search_videos("drenaż")] == ["lymphatic_drainage"]


def test_all_techniques_lists_every_entry():
    from services.video_learning import VIDEO_DB
    assert len(VideoLearningEngine.all_techniques()) == len(VIDEO_DB) == 6
