import numpy as np


def read_pi_meta(pi_dir):
    with open(pi_dir, 'r') as file:  # Read meta data from first two lines into a dictionary
        line1 = file.readline()[:-1]
        line2 = file.readline()[:-1]
        pieces = line2.split(',')
        if '{' in line2:
            curly_start = np.where(np.array([p[0] for p in pieces]) == '{')[0]
            curly_end = np.where(np.array([p[-1] for p in pieces]) == '}')[0]
            pieces_list = []
            sub_piece = []
            for i in range(len(pieces)):
                if curly_start[0] <= i <= curly_end[0] or curly_start[1] <= i <= curly_end[1]:
                    sub_piece.append(pieces[i])
                else:
                    pieces_list.append(pieces[i])
                if i in curly_end:
                    string = ','.join(sub_piece)
                    try:
                        s, e = string.index('<'), string.index('>')
                        string = string[:s] + "'exp_decreasing'" + string[e + 1:]
                    except Exception as e:
                        pass
                    pieces_list.append(eval(string))
                    sub_piece = []
        else:
            pieces_list = line2.split(',')
    info = dict(zip(line1.split(','), pieces_list))
    return info
