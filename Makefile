.PHONY: help setup extract guards viz verify docs visualize visualize-strict bundle dashboard clean test-system

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "BoR-SDK Visual Proof Pipeline - Makefile targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

setup: ## Install dependencies (requirements.txt + requirements-viz.txt)
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-viz.txt
	@echo "✅ Setup complete"

extract: ## Run data extraction (visual_data.json)
	@echo "🔍 Extracting trace data..."
	python extract_trace_data.py

guards: extract ## Compute hallucination guards
	@echo "🧠 Computing hallucination guards..."
	python compute_hallucination_guards.py

viz: guards ## Generate all visualizations
	@echo "🎨 Generating visualizations..."
	python generate_all_visualizations.py

verify: viz ## Verify visual integrity
	@echo "🔐 Verifying visual integrity..."
	python verify_visual_integrity.py

docs: verify ## Assemble documentation
	@echo "📝 Assembling documentation..."
	python assemble_visual_proof.py

visualize: docs ## Run complete pipeline (extract → guards → viz → verify → docs)
	@echo ""
	@echo "✅ Complete visualization pipeline executed successfully!"
	@echo "   View results: docs/visual_proof.md"

visualize-strict: ## Run complete pipeline with strict verification (fail on warnings)
	@echo "🔒 Running pipeline in strict mode..."
	@./run_visual_pipeline.sh --strict

bundle: ## Create timestamped artifact bundle using orchestrator
	@./run_visual_pipeline.sh --strict

dashboard: ## Launch interactive web dashboard
	@echo "🌐 Launching interactive dashboard..."
	@command -v streamlit >/dev/null 2>&1 || { echo "❌ Streamlit not installed. Run: pip install streamlit plotly pandas"; exit 1; }
	streamlit run interactive_visual_dashboard.py

clean: ## Remove generated artifacts
	@echo "🧹 Cleaning artifacts..."
	rm -f visual_data.json visual_verification_report.json
	rm -rf figures/
	rm -rf docs/visual_proof.md
	@echo "✅ Cleanup complete"

clean-all: clean ## Remove all artifacts including bundles
	@echo "🧹 Deep cleaning (including bundles)..."
	rm -rf visual_proofs/
	@echo "✅ Deep cleanup complete"

test-system: ## Run complete system verification test
	@./test_system.sh
