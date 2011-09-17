LOCAL_BIN=~/local/bin
GNOME_APPLICATION_DIR=~/.local/share/applications
GNOME_DESKTOP_FILE= $(wildcard *.desktop)
EXEC=pimpc.sh

install:bin gnome

bin:
	@ echo "Script $(EXEC) installed in $(LOCAL_BIN)"
	@ install $(EXEC)  $(LOCAL_BIN) 

gnome:
	@ echo "Gnome file associations add for:" $(GNOME_DESKTOP_FILE)
	@ install $(GNOME_DESKTOP_FILE) $(GNOME_APPLICATION_DIR)/
	@ update-desktop-database $(GNOME_APPLICATION_DIR)
	@ echo "warning: gnome checks PATH variable to launch a program, it then must contain "$(LOCAL_BIN)



clean:
	rm -f $(LOCAL_BIN)/$(EXEC)
	rm -f $(GNOME_APPLICATION_DIR)/[0-9]-pimpc*desktop
	update-desktop-database $(GNOME_APPLICATION_DIR)