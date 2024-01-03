"""provides a class for managing the PDF transform stack during "layout" mode
text extraction.
"""
from collections import ChainMap, Counter
from typing import Counter as CounterType, ChainMap as ChainMapType, List, Union

from .. import mult


from ._fonts import Font, TextStateParams


class XformStack:
    """cm/tm transformation matrix manager

    Attributes:
        xfrm_stack (ChainMap): ChainMap of cm/tm transformation matrices
        q_queue (Counter[int]): Counter of q operators
        q_depth (List[int]): list of q operator nesting levels
        Tc (float): character spacing
        Tw (float): word spacing
        Tz (int): horizontal scaling
        TL (float): leading
        Ts (float): text rise
        font (Font): font object
        font_size (int | float): font size

    Methods:
        raw_xform: only a/b/c/d/e/f matrix params
        new_xform: a/b/c/d/e/f matrix params + 'is_text' and 'is_render' keys
        reset_tm: clear all xforms from chainmap having is_text==True
        reset_trm: clear all xforms from chainmap having is_render==True
        remove_q: rewind to stack prior state after closing a 'q' with internal 'cm' ops
        add_q: add another level to q_queue
        add_cm: concatenate an additional transform matrix
        add_tm: append a text transform matrix
        add_trm: append a text rendering transform matrix
        text_state_params: current text state parameters
        effective_xform: the current effective transform account for both cm and text xforms
        flip_vertical: True if page is upside down
        xmaps: internal ChainMap 'maps' property
    """

    def __init__(self) -> None:
        self.xfrm_stack = ChainMap(self.new_xform())
        self.q_queue: CounterType[int] = Counter()
        self.q_depth = [0]
        self.Tc: float = 0.0
        self.Tw: float = 0.0
        self.Tz: float = 100.0
        self.TL: float = 0.0
        self.Ts: float = 0.0
        self.font: Union[Font, None] = None
        self.font_size: Union[int, float, None] = None

    def text_state_params(self, txt: str = "") -> TextStateParams:
        """current text state parameters

        Returns:
            TextStateParams: current text state parameters
        """
        if self.font is None or self.font_size is None:
            raise ValueError("font and font_size not set: is PDF missing a Tf operator?")
        return TextStateParams(
            txt,
            self.font,
            self.font_size,
            self.Tc,
            self.Tw,
            self.Tz,
            self.TL,
            self.Ts,
            self.effective_xform,
        )

    @staticmethod
    def raw_xform(_a=1.0, _b=0.0, _c=0.0, _d=1.0, _e=0.0, _f=0.0):
        """only a/b/c/d/e/f matrix params"""
        return dict(zip(range(6), map(float, (_a, _b, _c, _d, _e, _f))))

    @staticmethod
    def new_xform(
        _a=1.0, _b=0.0, _c=0.0, _d=1.0, _e=0.0, _f=0.0, is_text=False, is_render=False
    ):
        """a/b/c/d/e/f matrix params + 'is_text' key"""
        return dict(
            XformStack.raw_xform(_a, _b, _c, _d, _e, _f),
            is_text=is_text,
            is_render=is_render,
        )

    def reset_tm(self) -> ChainMapType[Union[int, str], Union[float, bool]]:
        """clear all xforms from chainmap having is_text==True"""
        while self.xfrm_stack.maps[0]["is_text"] or self.xfrm_stack.maps[0]["is_render"]:
            self.xfrm_stack = self.xfrm_stack.parents
        return self.xfrm_stack

    def reset_trm(self) -> ChainMapType[Union[int, str], Union[float, bool]]:
        """clear all xforms from chainmap having is_render==True"""
        while self.xfrm_stack.maps[0]["is_render"]:
            self.xfrm_stack = self.xfrm_stack.parents
        return self.xfrm_stack

    def remove_q(self) -> ChainMapType[Union[int, str], Union[float, bool]]:
        """rewind to stack prior state after closing a 'q' with internal 'cm' ops"""
        self.xfrm_stack = self.reset_tm()
        self.xfrm_stack.maps = self.xfrm_stack.maps[self.q_queue.pop(self.q_depth.pop(), 0) :]
        return self.xfrm_stack

    def add_q(self):
        """add another level to q_queue"""
        self.q_depth.append(len(self.q_depth))

    def add_cm(self, *args):
        """concatenate an additional transform matrix"""
        self.xfrm_stack = self.reset_tm()
        self.q_queue.update(self.q_depth[-1:])
        self.xfrm_stack = self.xfrm_stack.new_child(self.new_xform(*args))
        return self.xfrm_stack

    def add_tm(self, operands: List[Union[float, int]]):
        """append a text transform matrix"""
        if len(operands) == 2:  # this is a Td operator
            operands = [1.0, 0.0, 0.0, 1.0, *operands]
        self.xfrm_stack = self.xfrm_stack.new_child(
            self.new_xform(*operands, is_text=True)  # type: ignore  # mypy issue
        )
        return self.xfrm_stack

    def add_trm(self, operands: List[Union[float, int]]):
        """append a text rendering transform matrix"""
        if len(operands) == 2:  # this is a Td operator
            operands = [1.0, 0.0, 0.0, 1.0, *operands]
        self.xfrm_stack = self.xfrm_stack.new_child(
            self.new_xform(*operands, is_text=True, is_render=True)  # type: ignore  # mypy issue
        )
        return self.xfrm_stack

    @property
    def effective_xform(self) -> List[float]:
        """the current effective transform accounting for cm, tm, and trm xforms"""
        eff_xform = [*self.xfrm_stack.maps[0].values()]
        for xform in self.xfrm_stack.maps[1:]:
            eff_xform = mult(eff_xform, xform)  # type: ignore
        return eff_xform

    @property
    def flip_vertical(self) -> bool:
        """True if page is upside down"""
        return self.effective_xform[3] < -1e-6  # copy behavior of orient() func

    @property
    def xmaps(self):
        """internal ChainMap 'maps' property"""
        return self.xfrm_stack.maps
