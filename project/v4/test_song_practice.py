import unittest
from train_songs import clip

class SongPracticeTests(unittest.TestCase):
    def test_partition_keeps_every_onset_once_including_unassigned(self):
        notes=[dict(id=i,start=t,end=t+1,pitch=60,leg=-1 if i==2 else 0)
               for i,t in enumerate([0.,3.999,4.,8.])]
        clips=[clip(notes,x)[0] for x in [0.,4.,8.]]
        self.assertEqual([n['id'] for c in clips for n in c],[0,1,2,3])
        self.assertEqual(clips[1][0]['leg'],-1)
        self.assertEqual(clips[1][0]['start'],.4)

    def test_preserve_long_note_release_and_source(self):
        source=dict(id=8,start=4.,end=12.,pitch=65,leg=2)
        notes,d=clip([source],4.)
        self.assertAlmostEqual(notes[0]['end']-notes[0]['start'],8.)
        self.assertGreater(d,notes[0]['end'])
        self.assertEqual(source['start'],4.)

if __name__=='__main__': unittest.main()
