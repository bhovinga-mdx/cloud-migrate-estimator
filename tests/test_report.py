"""Tests for report generation."""


from estimator.report import render_report


class TestRenderReport:
    def test_renders_markdown(
        self, sample_extraction, sample_architecture, sample_estimate, sample_gaps, rate_card, aws_baselines
    ):
        report = render_report(
            extraction=sample_extraction,
            architecture=sample_architecture,
            estimate=sample_estimate,
            gaps=sample_gaps,
            rate_card=rate_card,
            aws_baselines=aws_baselines,
        )
        assert isinstance(report, str)
        assert len(report) > 0

    def test_contains_executive_summary(
        self, sample_extraction, sample_architecture, sample_estimate, sample_gaps, rate_card, aws_baselines
    ):
        report = render_report(
            extraction=sample_extraction,
            architecture=sample_architecture,
            estimate=sample_estimate,
            gaps=sample_gaps,
            rate_card=rate_card,
            aws_baselines=aws_baselines,
        )
        assert "## Executive Summary" in report

    def test_contains_cost_table(
        self, sample_extraction, sample_architecture, sample_estimate, sample_gaps, rate_card, aws_baselines
    ):
        report = render_report(
            extraction=sample_extraction,
            architecture=sample_architecture,
            estimate=sample_estimate,
            gaps=sample_gaps,
            rate_card=rate_card,
            aws_baselines=aws_baselines,
        )
        assert "Optimistic" in report
        assert "Likely" in report
        assert "Pessimistic" in report

    def test_contains_gap_analysis(
        self, sample_extraction, sample_architecture, sample_estimate, sample_gaps, rate_card, aws_baselines
    ):
        report = render_report(
            extraction=sample_extraction,
            architecture=sample_architecture,
            estimate=sample_estimate,
            gaps=sample_gaps,
            rate_card=rate_card,
            aws_baselines=aws_baselines,
        )
        assert "## Gap Analysis" in report
        assert "Follow-Up Questions" in report

    def test_contains_roles_table(
        self, sample_extraction, sample_architecture, sample_estimate, sample_gaps, rate_card, aws_baselines
    ):
        report = render_report(
            extraction=sample_extraction,
            architecture=sample_architecture,
            estimate=sample_estimate,
            gaps=sample_gaps,
            rate_card=rate_card,
            aws_baselines=aws_baselines,
        )
        assert "Solutions Architect" in report
        assert "Cloud Engineer" in report

    def test_contains_generated_date(
        self, sample_extraction, sample_architecture, sample_estimate, sample_gaps, rate_card, aws_baselines
    ):
        report = render_report(
            extraction=sample_extraction,
            architecture=sample_architecture,
            estimate=sample_estimate,
            gaps=sample_gaps,
            rate_card=rate_card,
            aws_baselines=aws_baselines,
        )
        assert "**Generated:**" in report

    def test_contains_disclaimer(
        self, sample_extraction, sample_architecture, sample_estimate, sample_gaps, rate_card, aws_baselines
    ):
        report = render_report(
            extraction=sample_extraction,
            architecture=sample_architecture,
            estimate=sample_estimate,
            gaps=sample_gaps,
            rate_card=rate_card,
            aws_baselines=aws_baselines,
        )
        assert "reviewed by a qualified engineer" in report
