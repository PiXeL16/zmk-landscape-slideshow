# ZMK Landscape Art Gallery Makefile
# Automates the art generation workflow

.PHONY: help install generate art clean backup restore setup test lint

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
ART_DIR := art
WIDGETS_DIR := boards/shields/nice_view_custom/widgets
ART_FILE := $(WIDGETS_DIR)/art.c
PERIPHERAL_FILE := $(WIDGETS_DIR)/peripheral_status.c
BACKUP_DIR := .backup
SCRIPT := generate_art.py

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)ZMK Landscape Art Gallery Generator$(NC)"
	@echo "=================================="
	@echo ""
	@echo "$(YELLOW)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-12s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  1. make setup     # Initial setup"
	@echo "  2. Add images to $(ART_DIR)/"
	@echo "  3. make generate  # Generate art gallery"

setup: ## Initial setup - install dependencies and create directories
	@echo "$(BLUE)Setting up ZMK Art Generation environment...$(NC)"
	@mkdir -p $(ART_DIR)
	@mkdir -p $(BACKUP_DIR)
	@$(MAKE) install
	@echo "$(GREEN)Setup complete!$(NC)"
	@echo "$(YELLOW)Next step: Add your images to the $(ART_DIR)/ folder$(NC)"

install: ## Install Python dependencies
	@echo "$(BLUE)Installing Python dependencies...$(NC)"
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed$(NC)"

generate: backup ## Generate art.c from images in art/ folder (with auto-rename)
	@echo "$(BLUE)Generating art gallery from images...$(NC)"
	@if [ ! -d "$(ART_DIR)" ]; then \
		echo "$(RED)Error: $(ART_DIR) directory not found!$(NC)"; \
		echo "$(YELLOW)Run 'make setup' first$(NC)"; \
		exit 1; \
	fi
	@if [ -z "$$(find $(ART_DIR) -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.bmp' -o -iname '*.gif' \) 2>/dev/null)" ]; then \
		echo "$(RED)Error: No supported image files found in $(ART_DIR)/$(NC)"; \
		echo "$(YELLOW)Supported formats: PNG, JPG, JPEG, BMP, GIF$(NC)"; \
		exit 1; \
	fi
	@$(PYTHON) $(SCRIPT)
	@echo "$(GREEN)Art gallery generated successfully!$(NC)"


art: generate ## Alias for generate command

rename-only: rename-images ## Alias for rename-images command

backup: ## Backup current art.c and peripheral_status.c files
	@echo "$(BLUE)Backing up current files...$(NC)"
	@mkdir -p $(BACKUP_DIR)
	@if [ -f "$(ART_FILE)" ]; then \
		cp "$(ART_FILE)" "$(BACKUP_DIR)/art.c.backup.$$(date +%Y%m%d_%H%M%S)"; \
		echo "$(GREEN)Backed up $(ART_FILE)$(NC)"; \
	fi
	@if [ -f "$(PERIPHERAL_FILE)" ]; then \
		cp "$(PERIPHERAL_FILE)" "$(BACKUP_DIR)/peripheral_status.c.backup.$$(date +%Y%m%d_%H%M%S)"; \
		echo "$(GREEN)Backed up $(PERIPHERAL_FILE)$(NC)"; \
	fi

restore: ## Restore from the most recent backup
	@echo "$(BLUE)Restoring from backup...$(NC)"
	@if [ -z "$$(ls -A $(BACKUP_DIR)/art.c.backup.* 2>/dev/null)" ]; then \
		echo "$(RED)Error: No backup files found in $(BACKUP_DIR)/$(NC)"; \
		exit 1; \
	fi
	@LATEST_ART=$$(ls -t $(BACKUP_DIR)/art.c.backup.* | head -n1); \
	LATEST_PERIPHERAL=$$(ls -t $(BACKUP_DIR)/peripheral_status.c.backup.* | head -n1); \
	cp "$$LATEST_ART" "$(ART_FILE)"; \
	cp "$$LATEST_PERIPHERAL" "$(PERIPHERAL_FILE)"; \
	echo "$(GREEN)Restored from backup: $$(basename $$LATEST_ART)$(NC)"

clean: ## Clean up generated files and backups
	@echo "$(BLUE)Cleaning up...$(NC)"
	@rm -rf $(BACKUP_DIR)
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete
	@echo "$(GREEN)Cleanup complete$(NC)"

test: ## Test the script with sample images (requires images in art/ folder)
	@echo "$(BLUE)Testing art generation...$(NC)"
	@if [ -z "$$(find $(ART_DIR) -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.bmp' -o -iname '*.gif' \) 2>/dev/null)" ]; then \
		echo "$(YELLOW)No test images found. Copying sample images...$(NC)"; \
		cp assets/*.png assets/*.jpg $(ART_DIR)/ 2>/dev/null || true; \
	fi
	@$(PYTHON) $(SCRIPT)
	@echo "$(GREEN)Test completed$(NC)"

quality-check: ## Compare before/after processing quality  
	@echo "$(BLUE)Generating quality comparison...$(NC)"
	@$(PYTHON) -c "from generate_art import *; from PIL import Image; files = get_image_files(); [print(f'  image{i}: {Image.open(f).size} -> 68x140 (reduction: {(Image.open(f).size[0]*Image.open(f).size[1])/(68*140):.1f}x)') for i, f in enumerate(files, 1)]"
	@echo "$(GREEN)Quality check completed$(NC)"

compare-methods: ## Compare different scaling methods side-by-side
	@echo "$(BLUE)Comparing scaling methods...$(NC)"
	@$(PYTHON) compare_methods.py
	@echo "$(GREEN)Method comparison completed - check art/method_comparison/$(NC)"

test-aspect-ratio: ## Test with and without aspect ratio preservation
	@echo "$(BLUE)Comparing aspect ratio preservation...$(NC)"
	@$(PYTHON) test_aspect_ratio.py
	@echo "$(GREEN)Aspect ratio test completed - check art/aspect_comparison/$(NC)"

lint: ## Check Python code with basic syntax validation
	@echo "$(BLUE)Checking Python syntax...$(NC)"
	@$(PYTHON) -m py_compile $(SCRIPT)
	@echo "$(GREEN)Python syntax OK$(NC)"

info: ## Show current project status
	@echo "$(BLUE)ZMK Art Generation Status$(NC)"
	@echo "========================"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Art directory: $(ART_DIR)/"
	@echo "Images found: $$(ls -1 $(ART_DIR)/*.png $(ART_DIR)/*.jpg $(ART_DIR)/*.jpeg $(ART_DIR)/*.bmp $(ART_DIR)/*.gif 2>/dev/null | wc -l | xargs)"
	@echo "Generated files:"
	@echo "  $(ART_FILE): $$(if [ -f $(ART_FILE) ]; then echo 'EXISTS'; else echo 'NOT FOUND'; fi)"
	@echo "  $(PERIPHERAL_FILE): $$(if [ -f $(PERIPHERAL_FILE) ]; then echo 'EXISTS'; else echo 'NOT FOUND'; fi)"
	@echo "Backups: $$(ls -1 $(BACKUP_DIR)/ 2>/dev/null | wc -l | xargs) files"

watch: ## Watch art directory for changes and auto-regenerate (requires fswatch)
	@echo "$(BLUE)Watching $(ART_DIR)/ for changes...$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@if ! command -v fswatch >/dev/null 2>&1; then \
		echo "$(RED)Error: fswatch not found. Install with: brew install fswatch$(NC)"; \
		exit 1; \
	fi
	@fswatch -o $(ART_DIR) | xargs -n1 -I{} make generate

# Development targets
dev-setup: setup ## Setup development environment with additional tools
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@$(PIP) install black flake8 2>/dev/null || echo "$(YELLOW)Note: black/flake8 not installed (optional)$(NC)"
	@echo "$(GREEN)Development setup complete$(NC)"

format: ## Format Python code (requires black)
	@echo "$(BLUE)Formatting Python code...$(NC)"
	@black $(SCRIPT) 2>/dev/null || echo "$(YELLOW)black not installed - skipping format$(NC)"

# Safety check before generating
check-images: ## Verify images and show current naming
	@echo "$(BLUE)Checking images in $(ART_DIR)/...$(NC)"
	@echo "$(YELLOW)Current images (in processing order):$(NC)"
	@counter=1; \
	for img in $$(find $(ART_DIR) -maxdepth 1 -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.bmp" -o -iname "*.gif" \) | sort); do \
		if [ -f "$$img" ]; then \
			name=$$(basename "$$img"); \
			echo "  $(GREEN)$$counter.$(NC) $$name -> image$$counter"; \
			counter=$$((counter + 1)); \
		fi; \
	done
	@echo ""
	@echo "$(YELLOW)Note:$(NC) Images are automatically renamed to image1, image2, etc. during generation"
	@echo "$(YELLOW)Tip:$(NC) High contrast images work best for 1-bit conversion"

preview-images: ## Generate preview images showing 1-bit conversion
	@echo "$(BLUE)Generating 1-bit conversion previews...$(NC)"
	@$(PYTHON) -c "from generate_art import *; import sys; image_files = get_image_files(); save_processed_previews(image_files) if image_files else print('No images found!')"
	@echo "$(GREEN)Previews generated in $(ART_DIR)/previews/$(NC)"

rename-images: ## Rename all images to follow standard naming convention (01_name.ext)
	@echo "$(BLUE)Renaming images to standard convention...$(NC)"
	@counter=1; \
	find $(ART_DIR) -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.bmp" -o -iname "*.gif" \) | \
	sort | \
	while read -r img; do \
		name=$$(basename "$$img"); \
		if [[ ! "$$name" =~ ^[0-9][0-9][_-] ]]; then \
			ext="$${name##*.}"; \
			base="$${name%.*}"; \
			clean_base=$$(echo "$$base" | sed 's/[^a-zA-Z0-9]/_/g' | sed 's/__*/_/g' | sed 's/^_//;s/_$$//'); \
			newname=$$(printf "%02d_%s.%s" $$counter "$$clean_base" "$$ext"); \
			if mv "$$img" "$(ART_DIR)/$$newname" 2>/dev/null; then \
				echo "  $(GREEN)Renamed:$(NC) \"$$name\" -> \"$$newname\""; \
			else \
				echo "  $(RED)Failed:$(NC) \"$$name\""; \
			fi; \
		else \
			echo "  $(BLUE)Skipped:$(NC) \"$$name\" (already properly named)"; \
		fi; \
		counter=$$((counter + 1)); \
	done
	@echo "$(GREEN)Renaming complete!$(NC)"
