APP = CAMOnion
UI_SRC_DIR = designer

RESOURCE_QRC = resources.qrc
CAMO_RESOURCES_DIR = $(APP)/resources/
CAMO_RESOURCES = $(CAMO_RESOURCES_DIR)/camo_resources.py
BUILD_DIST = dist/CAMOnion
INSTALLER_FILE = installer/getCAMO.exe
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

.PHONY : resources
resource: $(CAMO_RESOURCES)

$(CAMO_RESOURCES) : $(RESOURCE_QRC)
	rm -f $@
	touch $(CAMO_RESOURCES_DIR)
	pyrcc5 -o $@ $<

.PHONY: deploy
deploy : $(INSTALLER_FILE)
	cp installer/getCAMO.exe "F:/CNC DATA/CAMOnion/"

$(INSTALLER_FILE): exe
	compil32 /cc "getcamo.iss"

.PHONY : installer
installer : $(INSTALLER_FILE)


BUILD_DIST: exe

.PHONY : exe
exe:
	pyinstaller main.py -w -i img/icon.ico -n "CAMOnion" --noconfirm --hidden-import sqlalchemy.ext.baked


## variables: 	see them
.PHONY : variables
variables :
	@echo CAMO_RESOURCES: $(CAMO_RESOURCES)
	@echo UI_SRC_FILES: $(UI_SRC_FILES)
	@echo UI_FILES: $(UI_FILES)
