import argparse
import pickle
from bsparser import load_preproc_dataset

FINGERS = {'1': 'RP', '2': 'RR', '3': 'RM', '4':'RI', '5':'RT', '6':'L'}

def save_dat(obj, fname):

    with open(fname, 'wb') as _: pickle.dump(obj, _, pickle.HIGHEST_PROTOCOL)
    return True

def get_input():

    print("1: Pinky\t2:Ring\t3:Middle\t4:Index\t5:Thumb\t6:Other")
    print("quit: quit\nb: back")
    print("goto X: skip to event X")

    inp = '0'

    while inp not in ['1', '2', '3', '4', '5', '6', 's', 'quit', 'f', 'b']:

        if inp != '0':
            print('try again')
        inp = input()

        if inp[:4] == 'goto':
            inp = inp.split(" ")
            return int(inp[1])

    if inp == 'quit':
        inp = input('"y" to confirm\n')
        if inp == 'y':
            exit()
        else:
            inp = get_input()

    return inp


def label_events(fname):

    tname = fname[:-4] + '.trg'
    evts = load_preproc_dataset(fname, filt=False, load=False)

    cur_event = -1
    increment = 1
    inp = None

    done = False
    while not done:

        print("\n" * 5)
        if inp in ['1', '2', '3', '4', '5', '6']:
            evts.set_event(cur_event, FINGERS[inp])
            print("set event %s as %s" % (cur_event, FINGERS[inp]))
        elif inp == 'b':
            increment = -1
        if save_dat(evts, tname): print('saved')


        if -1 <= cur_event < len(evts):
            cur_event += increment
            while -1 < cur_event < len(evts) and evts[cur_event].type == 'TS':
                cur_event += increment

        if isinstance(inp, int) and -1 <= inp < len(evts):
            cur_event = inp

        increment = 1
        this_evt = evts[cur_event]

        print("File: %s" % fname)
        print("Event %s / %s" % (cur_event, len(evts)))
        print("Key: %s\nLabel: %s" % (this_evt.key, this_evt.type))

        inp = get_input()




    return evts

parser = argparse.ArgumentParser()
parser.add_argument('fname')
args = parser.parse_args()
fname = args.fname

x = label_events(fname)
