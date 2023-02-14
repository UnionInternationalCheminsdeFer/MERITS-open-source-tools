from unittest import TestCase

from merits.edifact.definition_model import Segment
from merits.edifact.object_model import DataLeaf
from merits.edifact.segment_format import SegmentFormat
from merits.edifact.segment_writer import SegmentWriter
from merits.skdupd import definition


class TestSegmentWriter(TestCase):

    def test_to_edifact(self):
        segment_definition = Segment(
            node_id="0000",
            name="TST",
            format="""
            TST
            +a_0
                *b_1
                    :c_2
                    :d_2
                *e_1
                    :f_2
                    :
            +g_0
                    :h_2
                    :
                    :i_2
            """,
        )
        config = definition.edifact_definition.config
        segment_format = SegmentFormat(
            definition=segment_definition,
            config=config,
        )

        obj = SegmentWriter()

        leaf = DataLeaf(
            path="TST",
            segment_format=segment_format,
        )
        for name in ("a_0", "f_2", "g_0", "h_2"):
            leaf.set(name, name + "_value")

        actual = obj.to_edifact(leaf)
        expected = "TST+a_0_value**:f_2_value+g_0_value:h_2_value'"
        self.assertEqual(expected, actual)
