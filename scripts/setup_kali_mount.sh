#!/usr/bin/env bash
#
# setup_kali_mount.sh — mount host ~/.rick_mcp into Kali at /home/kali/.rick_mcp
#
# Mirrors the host content repo into the Kali VM at the same logical path so
# identity files, vault, and notes sync bidirectionally. Type findings in Kali,
# Obsidian on the host indexes them live.
#
# Prerequisites (one-time, on the macOS host in VMware Fusion):
#   1. Virtual Machine → Settings → Sharing → enable Shared Folders
#   2. Add the host's ~/.rick_mcp directory
#   3. Name the share `rick_mcp` (must match $SHARE_NAME below)
#
# Run this script inside Kali after the share is configured on the host:
#
#   bash scripts/setup_kali_mount.sh
#
# Idempotent — safe to re-run. Parameterized via env vars for non-default setups.
#
# Adapt for VirtualBox / Parallels / UTM by swapping fuse.vmhgfs-fuse for the
# guest-tools driver of that platform; the rest stays the same.

set -euo pipefail

SHARE_NAME="${SHARE_NAME:-rick_mcp}"
MOUNT_POINT="${MOUNT_POINT:-/home/kali/.rick_mcp}"
TARGET_UID="${TARGET_UID:-1000}"
TARGET_GID="${TARGET_GID:-1000}"

FSTAB_ENTRY=".host:/${SHARE_NAME} ${MOUNT_POINT} fuse.vmhgfs-fuse allow_other,defaults,uid=${TARGET_UID},gid=${TARGET_GID} 0 0"

log() { printf '[%s] %s\n' "$1" "$2"; }

log "*" "rick_mcp Kali mount setup"
log " " "  share:       .host:/${SHARE_NAME}"
log " " "  mount point: ${MOUNT_POINT}"
log " " "  uid/gid:     ${TARGET_UID}/${TARGET_GID}"
echo

# 1. Ensure vmhgfs-fuse is installed
if ! command -v vmhgfs-fuse >/dev/null 2>&1; then
    log "*" "Installing open-vm-tools-desktop..."
    sudo apt update
    sudo apt install -y open-vm-tools-desktop
else
    log "ok" "vmhgfs-fuse already installed"
fi

# 2. Preflight — verify the host-side share is actually visible from the guest.
# Without this check, mount can "succeed" (fstab parses) while the FUSE source
# is unreachable, leaving a broken mount where ls returns "No such file or directory".
if ! vmware-hgfsclient | grep -qx "${SHARE_NAME}"; then
    log "!" "Share '${SHARE_NAME}' not visible from the guest."
    log " " "  Run 'vmware-hgfsclient' to see what shares the host is currently exposing."
    log " " ""
    log " " "  Fix on the macOS host:"
    log " " "    VMware Fusion → Virtual Machine → Settings → Sharing"
    log " " "    Enable Shared Folders, add ~/.rick_mcp, name the share '${SHARE_NAME}'"
    log " " "    Restart the VM if the share was added while it was running."
    exit 1
fi
log "ok" "host share '${SHARE_NAME}' is visible"

# 3. Create mount point
if [ ! -d "${MOUNT_POINT}" ]; then
    sudo mkdir -p "${MOUNT_POINT}"
    sudo chown "${TARGET_UID}:${TARGET_GID}" "${MOUNT_POINT}"
    log "+" "created mount point ${MOUNT_POINT}"
else
    log "ok" "mount point exists: ${MOUNT_POINT}"
fi

# 4. Add fstab entry (idempotent — match by mount point, not full line)
if grep -qE "[[:space:]]${MOUNT_POINT}[[:space:]]" /etc/fstab; then
    log "ok" "/etc/fstab already has an entry for ${MOUNT_POINT}"
else
    echo "${FSTAB_ENTRY}" | sudo tee -a /etc/fstab > /dev/null
    log "+" "added fstab entry"
fi

# 5. Mount
if mountpoint -q "${MOUNT_POINT}"; then
    log "ok" "already mounted"
else
    sudo mount "${MOUNT_POINT}"
    log "+" "mounted"
fi

# 6. Verify
echo
log "*" "Verification:"
ls -la "${MOUNT_POINT}" | head -8
echo

# Round-trip write test
TEST_FILE="${MOUNT_POINT}/.mount-test-$(date +%s)"
if touch "${TEST_FILE}" 2>/dev/null && [ -f "${TEST_FILE}" ]; then
    rm -f "${TEST_FILE}"
    log "ok" "write test passed (round-trip clean)"
else
    log "!" "write test FAILED — check uid/gid match and host share permissions"
    exit 1
fi

echo
log "done" "Mount ready."
log " " "  Edit engagement notes in Kali:"
log " " "    vim ${MOUNT_POINT}/vault/Engagements/<codename>.md"
log " " "  Obsidian on the host indexes changes live."
