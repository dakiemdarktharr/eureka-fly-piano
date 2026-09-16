import sys,unittest,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiments.input_events import midi_events
from experiments.run import events_for

class InputTests(unittest.TestCase):
    def test_midi_seconds_and_disclosed_reduction(self):
        import mido
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'synthetic.mid';mid=mido.MidiFile(ticks_per_beat=480);t=mido.MidiTrack();mid.tracks.append(t)
            t.append(mido.MetaMessage('set_tempo',tempo=500000,time=0))
            t.append(mido.Message('note_on',note=60,velocity=80,time=480))
            t.append(mido.Message('note_on',note=64,velocity=80,time=0));mid.save(p)
            e=midi_events(p);self.assertEqual(e['discarded_note_count'],1);self.assertEqual(len(e['events']),1);self.assertAlmostEqual(e['events'][0]['time'],.5)
    def test_event_order_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'events.json';p.write_text(json.dumps([{'key':0,'time':1},{'key':1,'time':.5}]))
            with self.assertRaises(ValueError):events_for({'event_file':str(p),'nkeys':8,'duration':8})

if __name__=='__main__':unittest.main()
