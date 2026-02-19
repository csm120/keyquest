"""Universal dialog system for KeyQuest.

Centralizes all wxPython dialog creation and management for consistency
and accessibility across the application.
"""

import traceback
import sys
import time
from pathlib import Path

try:
    import wx
    WX_AVAILABLE = True
except ImportError:
    WX_AVAILABLE = False
    print("wxPython not available - dialogs will print to console")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


def log_dialog_error(error_type, error_msg, tb_str):
    """Log dialog errors to a local diagnostics file."""
    try:
        log_file = Path("dialog_errors.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Dialog Error: {error_type}\n")
            f.write(f"Message: {error_msg}\n")
            f.write(f"Traceback:\n{tb_str}\n")
            f.write(f"{'='*60}\n")
    except:
        pass  # If logging fails, don't crash


def show_dialog(
    title,
    content,
    dialog_type="info",
    close_on_enter=True,
    close_on_escape=True,
    close_on_space=False,
):
    """Show an accessible dialog box with read-only text content.

    This is the universal dialog function used throughout KeyQuest for:
    - Game results/scores
    - Speed test results
    - Practice results
    - Lesson results
    - Game info (How to Play, Controls, Description)
    - Any other informational content

    Args:
        title: Dialog window title
        content: Content to display in the text box
        dialog_type: Type of dialog ("info", "results") - currently just for documentation

    Returns:
        None - Blocks until user closes dialog
    """
    if not WX_AVAILABLE:
        # Fallback: print to console
        print(f"\n{'=' * 60}")
        print(f"{title}")
        print('=' * 60)
        print(content)
        print('=' * 60)
        return

    dlg = None
    try:
        # wx.App should already exist (created at application startup)
        # If not, something is wrong - log and fail gracefully
        wx_app = wx.App.Get()
        if not wx_app:
            error_msg = "wx.App not initialized - dialogs won't work"
            log_dialog_error("wx.App check", error_msg, "No traceback - app not initialized")
            print(f"ERROR: {error_msg}")
            print(f"\n{title}\n{content}")
            return

        # Create dialog with no parent
        try:
            dlg = wx.Dialog(None, title=title,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
                           size=(600, 450))
        except Exception as e:
            log_dialog_error("wx.Dialog creation", f"Failed to create dialog: {e}", traceback.format_exc())
            raise

        # Create panel
        panel = wx.Panel(dlg)

        # Create read-only multiline text control
        text_ctrl = wx.TextCtrl(panel, value=content,
                               style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)

        # Set font based on dialog type
        if dialog_type == "results":
            # Monospace font for results (preserves alignment)
            font = wx.Font(11, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        else:
            # Default font for info
            font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text_ctrl.SetFont(font)

        # OK button
        ok_btn = wx.Button(panel, wx.ID_OK, "OK")
        if close_on_enter:
            ok_btn.SetDefault()

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        sizer.Add(ok_btn, 0, wx.ALL | wx.CENTER, 10)
        panel.SetSizer(sizer)

        # Guard flag to prevent multiple EndModal calls (crash prevention)
        dialog_closing = [False]

        # Close dialog safely (called after event handler completes)
        def close_dialog():
            if not dialog_closing[0]:
                dialog_closing[0] = True
                try:
                    dlg.EndModal(wx.ID_OK)
                except:
                    pass  # Dialog already closing

        # Bind Enter and Escape keys to close dialog
        def on_key(event):
            keycode = event.GetKeyCode()
            should_close = False
            if close_on_enter and keycode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
                should_close = True
            elif close_on_escape and keycode == wx.WXK_ESCAPE:
                should_close = True
            elif close_on_space and keycode == wx.WXK_SPACE:
                should_close = True

            if should_close:
                # Use CallAfter to close dialog AFTER this event handler completes
                # This prevents crashes from trying to unbind events while they're executing
                wx.CallAfter(close_dialog)
                return  # Don't skip event - we handled it
            else:
                event.Skip()

        # Bind OK button to prevent multiple clicks causing crash
        def on_ok(event):
            # Use CallAfter to close dialog AFTER this event handler completes
            # This prevents crashes from trying to unbind events while they're executing
            wx.CallAfter(close_dialog)

        try:
            dlg.Bind(wx.EVT_CHAR_HOOK, on_key)
            ok_btn.Bind(wx.EVT_BUTTON, on_ok)
        except Exception as e:
            log_dialog_error("Event binding", f"Failed to bind events: {e}", traceback.format_exc())
            # Continue anyway - dialog may still work with mouse

        # CRITICAL CHANGE: Do NOT pump pygame events while wx dialog is modal
        # This was causing crashes - let wx have full control during ShowModal
        # We'll clear pygame events AFTER the dialog closes instead

        # Center dialog
        try:
            dlg.Centre()
        except Exception as e:
            log_dialog_error("Dialog centering", f"Failed to center dialog: {e}", traceback.format_exc())

        # Show modal - this blocks until user closes it
        # wx has FULL control during this time - no pygame event pumping
        try:
            dlg.ShowModal()
        except Exception as e:
            log_dialog_error("ShowModal", f"ShowModal failed: {e}", traceback.format_exc())
            raise

    except Exception as e:
        # Log exception and fallback to console
        error_msg = f"Dialog error: {type(e).__name__}: {e}"
        tb_str = traceback.format_exc()
        print(error_msg)
        print(f"\n{title}")
        print(content)
        log_dialog_error(f"show_dialog({title})", error_msg, tb_str)
    finally:
        # Always destroy dialog after ShowModal returns
        if dlg is not None:
            try:
                dlg.Destroy()
            except Exception as e:
                log_dialog_error("Dialog destroy", f"Failed to destroy dialog: {e}", traceback.format_exc())

        # Clear pygame event queue (may have stale events from wx dialog)
        # Do this AFTER dialog is fully destroyed
        if PYGAME_AVAILABLE:
            try:
                pygame.event.clear()
            except Exception as e:
                log_dialog_error("Final pygame cleanup", f"Failed to clear pygame events: {e}", traceback.format_exc())


def show_info_dialog(title, content):
    """Show an informational dialog (How to Play, Controls, Description, etc.).

    Args:
        title: Dialog window title
        content: Content to display
    """
    show_dialog(title, content, dialog_type="info")


def show_results_dialog(
    title,
    content,
    close_on_enter=True,
    close_on_escape=True,
    close_on_space=False,
):
    """Show a results dialog (test results, game scores, lesson completion, etc.).

    Uses monospace font to preserve alignment of statistics.

    Args:
        title: Dialog window title
        content: Formatted results text
    """
    show_dialog(
        title,
        content,
        dialog_type="results",
        close_on_enter=close_on_enter,
        close_on_escape=close_on_escape,
        close_on_space=close_on_space,
    )
