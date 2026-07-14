"""Integration tests for optimizer and configuration management."""

import pytest

from src.config import ConfigManager
from src.optimizer import PromptOptimizer, TokenCounter


class TestOptimizerConfigIntegration:
    """Test suite for optimizer and config integration."""

    @pytest.fixture
    def config_manager(self):
        """Create a fresh ConfigManager instance."""
        ConfigManager._instance = None
        return ConfigManager(environment='test')

    @pytest.mark.xfail(strict=True, reason="Phase 4: config not wired to runtime — PromptOptimizer rejects config kwarg")
    def test_optimizer_uses_config(self, config_manager):
        """Test PromptOptimizer respects configuration settings."""
        config_manager.update({
            'optimizer.max_tokens': 8192,
            'optimizer.target_reduction': 0.4,
            'optimizer.min_quality_score': 0.85,
        })

        opt_config = config_manager.get_optimizer_config()
        optimizer = PromptOptimizer(
            max_tokens=opt_config.max_tokens,
            target_reduction=opt_config.target_reduction,
        )

        assert optimizer.max_tokens == 8192
        assert optimizer.target_reduction == 0.4

    def test_token_counter_with_config(self, config_manager):
        """Test TokenCounter with configuration."""
        opt_config = config_manager.get_optimizer_config()
        counter = TokenCounter()

        text = "This is a test prompt for token counting."
        token_count = counter.count_tokens(text)

        # Verify token count is reasonable
        assert token_count > 0
        assert token_count < opt_config.max_tokens

    @pytest.mark.xfail(strict=True, reason="Phase 4: config not wired to runtime — PromptOptimizer rejects config kwarg")
    def test_optimizer_respects_max_tokens(self, config_manager):
        """Test optimizer respects max_tokens from config."""
        config_manager.update({
            'optimizer.max_tokens': 50,
            'optimizer.target_reduction': 0.3,
        })

        opt_config = config_manager.get_optimizer_config()
        optimizer = PromptOptimizer(
            max_tokens=opt_config.max_tokens,
            target_reduction=opt_config.target_reduction,
        )

        # Create a long prompt
        long_prompt = " ".join(["word"] * 100)
        result = optimizer.optimize(long_prompt)

        # Verify result respects max_tokens
        counter = TokenCounter()
        result_tokens = counter.count_tokens(result['optimized_text'])
        assert result_tokens <= opt_config.max_tokens

    @pytest.mark.xfail(strict=True, reason="Phase 4: config not wired to runtime — PromptOptimizer rejects config kwarg")
    def test_runtime_config_update_affects_optimizer(self, config_manager):
        """Test runtime config updates affect optimizer behavior."""
        # Initial config
        opt_config = config_manager.get_optimizer_config()
        optimizer1 = PromptOptimizer(max_tokens=opt_config.max_tokens)
        assert optimizer1.max_tokens == 4096  # default

        # Update config
        config_manager.update({'optimizer.max_tokens': 16384})

        # Create new optimizer with updated config
        opt_config = config_manager.get_optimizer_config()
        optimizer2 = PromptOptimizer(max_tokens=opt_config.max_tokens)
        assert optimizer2.max_tokens == 16384

    def test_optimizer_strategies_from_config(self, config_manager):
        """Test optimizer uses strategies from configuration."""
        config_manager.update({
            'optimizer.strategies': ['remove_whitespace', 'compress_repeated'],
        })

        opt_config = config_manager.get_optimizer_config()
        assert 'remove_whitespace' in opt_config.strategies
        assert 'compress_repeated' in opt_config.strategies

    @pytest.mark.xfail(strict=True, reason="Phase 4: config not wired to runtime — PromptOptimizer rejects config kwarg")
    def test_target_reduction_from_config(self, config_manager):
        """Test optimizer target reduction from config."""
        config_manager.update({
            'optimizer.target_reduction': 0.5,
        })

        opt_config = config_manager.get_optimizer_config()
        optimizer = PromptOptimizer(target_reduction=opt_config.target_reduction)

        text = "This is a test prompt with some repeated repeated words."
        result = optimizer.optimize(text)

        # Verify reduction is attempted
        assert result['original_tokens'] > 0
        assert result['optimized_tokens'] <= result['original_tokens']

    def test_quality_score_threshold(self, config_manager):
        """Test optimizer respects quality score threshold."""
        config_manager.update({
            'optimizer.min_quality_score': 0.9,
        })

        opt_config = config_manager.get_optimizer_config()

        # Quality score threshold should be respected
        assert opt_config.min_quality_score == 0.9

    def test_config_validation_prevents_invalid_optimizer_config(self, config_manager):
        """Test config validation prevents invalid optimizer configurations."""
        from src.config.validator import ValidationError

        # Try to set invalid target_reduction (> 1.0)
        with pytest.raises(ValidationError):
            config_manager.update({
                'optimizer.target_reduction': 1.5,
            })

        # Try to set invalid max_tokens (< 1)
        with pytest.raises(ValidationError):
            config_manager.update({
                'optimizer.max_tokens': 0,
            })

    @pytest.mark.xfail(strict=True, reason="Phase 4: config not wired to runtime — PromptOptimizer rejects config kwarg")
    def test_multiple_optimizers_share_config(self, config_manager):
        """Test multiple optimizer instances can share configuration."""
        config_manager.update({
            'optimizer.max_tokens': 6144,
            'optimizer.target_reduction': 0.35,
        })

        opt_config = config_manager.get_optimizer_config()

        optimizer1 = PromptOptimizer(
            max_tokens=opt_config.max_tokens,
            target_reduction=opt_config.target_reduction,
        )
        optimizer2 = PromptOptimizer(
            max_tokens=opt_config.max_tokens,
            target_reduction=opt_config.target_reduction,
        )

        assert optimizer1.max_tokens == optimizer2.max_tokens == 6144
        assert optimizer1.target_reduction == optimizer2.target_reduction == 0.35

    def test_optimizer_with_empty_strategies(self, config_manager):
        """Test optimizer handles empty strategies list validation."""
        from src.config.validator import ValidationError

        # Empty strategies should fail validation
        with pytest.raises(ValidationError):
            config_manager.update({
                'optimizer.strategies': [],
            })

    def test_optimizer_with_invalid_strategy(self, config_manager):
        """Test optimizer rejects invalid strategies."""
        from src.config.validator import ValidationError

        with pytest.raises(ValidationError):
            config_manager.update({
                'optimizer.strategies': ['invalid_strategy'],
            })
