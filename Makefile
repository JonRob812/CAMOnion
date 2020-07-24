APP = CAMOnion
UI_SRC_DIR = designer

RESOURCE_QRC = resources.qrc
CAMO_RESOURCES = $(APP)/ui/camo_resources.py

UI_SRC_FILES = $(wildcard $(UI_SRC_DIR)/*.ui)
UI_FILES = $(patsubst $(UI_SRC_DIR)/%.ui, $(APP)/ui/%_ui.py, $(UI_SRC_FILES))

.PHONY : run
run: ui
	python main.py

.PHONY : ui
ui: $(UI_FILES)

$(APP)/ui/%_ui.py: $(UI_SRC_DIR)/%.ui
	rm -f $@
	pyuic5 -o $@ $<

.PHONY : resource
resource: $(CAMO_RESOURCES)

$(CAMO_RESOURCES) : $(RESOURCE_QRC)
	rm -f $@
	pyrcc5 -o $@ $<


## variables: 	see them
.PHONY : variables
variables :
	@echo CAMO_RESOURCES: $(CAMO_RESOURCES)
	@echo UI_SRC_FILES: $(UI_SRC_FILES)
	@echo UI_FILES: $(UI_FILES)
