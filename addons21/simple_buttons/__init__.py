import anki
from anki.hooks import addHook

import aqt
from aqt.utils import showInfo
from aqt.reviewer import Reviewer
from aqt.qt import *

from .stat import Stat


def advice(module, symbol, fn):
    setattr(module, symbol, anki.hooks.wrap(getattr(module, symbol), fn, "around"))


def _answerButtons(self, _old):
    def but(ease, label):
        return '''
            <td align=center>
              <button title="{title}">{label}</button>
            </td>
        '''.format(
            title = "Shortcut key: %s".format(ease),
            label = label,
            ease = ease
        )
    buf = "<center><table cellpading=0 cellspacing=0><tr>"
    for ease, label in [(1, "Again"), (2, "Done")]:
        buf += but(ease, label)
    buf += "</tr></table>"
    return buf

advice(Reviewer, "_answerButtons", _answerButtons)


def _shortcutKeys(self, _old):
    return [
        ("e", self.mw.onEditCurrent),
        (" ", self.onEnterKey),
        (Qt.Key_Return, self.onEnterKey),
        (Qt.Key_Enter, self.onEnterKey),
        ("r", self.replayAudio),
        (Qt.Key_F5, self.replayAudio),
        ("Ctrl+1", lambda: self.setFlag(1)),
        ("Ctrl+2", lambda: self.setFlag(2)),
        ("Ctrl+3", lambda: self.setFlag(3)),
        ("Ctrl+4", lambda: self.setFlag(4)),
        ("Ctrl+0", lambda: self.setFlag(0)),
        ("*", self.onMark),
        ("=", self.onBuryNote),
        ("-", self.onBuryCard),
        ("!", self.onSuspend),
        ("@", self.onSuspendCard),
        ("Ctrl+Delete", self.onDelete),
        ("v", self.onReplayRecorded),
        ("Shift+v", self.onRecordVoice),
        ("o", self.onOptions),
        ("1", lambda: again(self)),
        ("2", lambda: done(self)),
    ]

advice(Reviewer, "_shortcutKeys", _shortcutKeys)


def again(self):
    _answerCard(self, 1)


def done(self):
    curDeck = self.mw.col.conf['curDeck']
    timeTaken = self.card.timeTaken() / 1e3
    cardType = self.card.type
    id_ = "{}:{}".format(curDeck, cardType)
    Stat.add(id_, timeTaken)
    q = Stat.quantile(id_, timeTaken)
    if q < 0.8:
        ease = 4
    elif q < 0.95:
        ease = 3
    else:
        ease = 2
    _answerCard(self, ease)


addHook('reviewCleanup', lambda: Stat.save())


def _answerCard(self, ease):
    "Reschedule card and show next."
    if self.mw.state != "review":
        # showing resetRequired screen; ignore key
        return
    if self.state != "answer":
        return
    ease = min(ease, self.mw.col.sched.answerButtons(self.card))
    self.mw.col.sched.answerCard(self.card, ease)
    self._answeredIds.append(self.card.id)
    self.mw.autosave()
    self.nextCard()
