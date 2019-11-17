import os.path
from xml.dom import minidom
import sys
import math
from fontParts.world import *
from stemfont.tools.attributetools import *

def _is_glif(file_name):
    tokens = file_name.split('.')
    if len(tokens) != 2:
        return False
    return tokens[-1] == 'glif'

def ufo2mf(destPath, ufoPath=None):
    if ufoPath is None:
        font = CurrentFont()
    else:
        font = OpenFont(os.path.abspath(ufoPath), showInterface=False)

    DIR_UFO = os.path.join(font.path, "glyphs")

    destPath = os.path.abspath(destPath)
    DIR_METAFONT_RADICAL = os.path.join(destPath, "radical.mf")
    DIR_METAFONT_COMBINATION = os.path.join(destPath, "combination.mf")

    print("Target:", DIR_UFO)
    print("Destination Path:", destPath)
    # Remove exist Metafont file for renew
    try:
        os.remove(DIR_METAFONT_RADICAL)
        os.remove(DIR_METAFONT_COMBINATION)
    except:
        nothing = 0

    # Get glyphs from UFO and Convert to Metafont
    glyphs = [font for font in os.listdir(DIR_UFO) if _is_glif(font)]
    font_width = get_font_width(DIR_UFO, glyphs)
    for glyph in glyphs:
        glyph2mf(glyph, DIR_UFO, DIR_METAFONT_RADICAL, DIR_METAFONT_COMBINATION, font_width, font)
    return None

class Point:
    def __init__(self):
        self.name = ""
        self.idx = ""
        self.type = ""
        self.x = ""
        self.y = ""
        self.controlPoints = []
        self.dependX = ""
        self.dependY = ""
        self.penWidth = ""
        self.penHeight = ""
        self.startP = ""
        self.endP = ""
        self.serif = ""
        self.roundA = ""
        self.sound = ""
        self.char = ""
        self.double = ""
        self.formType = ""
        self.customer = ""

def _get_value_by_node(tag, attribute):
    node = xmlData.getElementsByTagName(tag)
    try:
        return node[0].attributes[attribute].value
    except:
        return None

def _float2str(value, decimal=4):
    str_val = str(float(value))
    return str_val[:str_val.find('.') + decimal]

class Num2Char:
    n2c = {
        '1':'o',
        '2':'t',
        '3':'h',
        '4':'u',
        '5':'i',
        '6':'s',
        '7':'v',
        '8':'g',
        '9':'n',
        '0':'z',
        '_':'_'
    }

    @classmethod
    def get_char(cls, number):
        return cls.n2c[number]

def _num2char(name):
    return ''.join([w if w.isalpha() else Num2Char.get_char(w) for w in list(name)])

def glyph2mf(glyphName, dirUFO, dirRadical, dirCombination, fontWidth, rfont):
    global xmlData

    totalNum = 400
    # Initialize points
    points = []
    for i in range(0, totalNum):
        points.append(Point())
        points[i].controlPoints = []

    # Get glyph's UFO file
    dirGlyph = os.path.join(dirUFO, glyphName)
    xmlData = minidom.parse(dirGlyph)

    # If combination file, create characters for using glyph
    components = xmlData.getElementsByTagName('component')

    # get glyph object
    rglyph = getglyphobject(glyphName, rfont)
    print(rglyph.name)

    if len(components) != 0:
        fp = open(dirCombination, "a")
        # Write beginchar
        # glyphName = getValueByNode('glyph', 'name')

        unicodeList = xmlData.getElementsByTagName("unicode")
        if len(unicodeList) == 1:  # Need Change if unicode is more than 1
            code = str(int(unicodeList[0].getAttribute('hex'), 16))
        # fp.write('\nbeginchar('  + code + ', Width#, Height#, 0);\n') #!!!!!!!!!!!!!!!
        fp.write(
            '\nbeginchar(' + code + ', max(firstWidth#, middleWidth#, finalWidth#), max(firstHeight#, middleHeight#, finalHeight#), 0);\n\n')
        # fp.write('\nbeginchar('  + glyphName + ', Width#, Height#, 0);\n')
        # fp.write("    currenttransform := identity slanted slant;\n\n") #!!!!!!!!!!!!!!!

        # Write componenet (changed)
        # cnt = 0
        for component in components:
            name = component.attributes['base'].value
            # *** Changed *** #
            # fp.write("    " + _num2char(name)) #!!!!!!!!!!!!!!!
            # Apply each parameter
            # if cnt == 0:
            #   fp.write("(firstMoveSizeOfH, firstMoveSizeOfV)\n")
            # elif cnt == 1:
            #   fp.write("(middleMoveSizeOfH, middleMoveSizeOfV)\n")
            # if cnt == 2:
            #   fp.write("(finalMoveSizeOfH, finalMoveSizeOfV)\n")
            # cnt = cnt + 1
            if name[-1] == 'C':
                fp.write("  currenttransform := identity slanted firstSlant;\n")
                fp.write("  " + _num2char(name))
                fp.write(
                    "(firstWidth, firstHeight, firstMoveSizeOfH, firstMoveSizeOfV, firstPenWidthRate, firstPenHeightRate, firstCurveRate, firstSerifRate, firstUnfillRate, false)\n")
                fp.write("  if firstUnfillRate > 0.0:\n")
                fp.write("    " + _num2char(name))
                fp.write(
                    "(firstWidth, firstHeight, firstMoveSizeOfH, firstMoveSizeOfV, firstPenWidthRate * firstUnfillRate, firstPenHeightRate * firstUnfillRate, firstCurveRate, firstSerifRate, firstUnfillRate, true)\n")
                fp.write("  fi\n\n")
            elif name[-1] == 'V':
                fp.write("  currenttransform := identity slanted middleSlant;\n")
                fp.write("  " + _num2char(name))
                fp.write(
                    "(middleWidth, middleHeight, middleMoveSizeOfH, middleMoveSizeOfV, middlePenWidthRate, middlePenHeightRate, middleCurveRate, middleSerifRate, middleUnfillRate, false)\n")
                fp.write("  if middleUnfillRate > 0.0:\n")
                fp.write("    " + _num2char(name))
                fp.write(
                    "(middleWidth, middleHeight, middleMoveSizeOfH, middleMoveSizeOfV, middlePenWidthRate * middleUnfillRate, middlePenHeightRate * middleUnfillRate, middleCurveRate, middleSerifRate, middleUnfillRate, true)\n")
                fp.write("  fi\n\n")
            elif name[-1] == 'F':
                fp.write("  currenttransform := identity slanted finalSlant;\n")
                fp.write("  " + _num2char(name))
                fp.write(
                    "(finalWidth, finalHeight, finalMoveSizeOfH, finalMoveSizeOfV, finalPenWidthRate, finalPenHeightRate, finalCurveRate, finalSerifRate, finalUnfillRate, false)\n")
                fp.write("  if finalUnfillRate > 0.0:\n")
                fp.write("    " + _num2char(name))
                fp.write(
                    "(finalWidth, finalHeight, finalMoveSizeOfH, finalMoveSizeOfV, finalPenWidthRate * finalUnfillRate, finalPenHeightRate * finalUnfillRate, finalCurveRate, finalSerifRate, finalUnfillRate, true)\n")
                fp.write("  fi\n\n")

        # Write end
        fp.write("endchar;\n");
        fp.close()
    else:  # If glyph file
        fp = open(dirRadical, "a")

        glyphName = _get_value_by_node('glyph', 'name')
        fp.write("% File parsed with MetaUFO %\n")
        # *** Changed *** #
        # fp.write('def ' + _num2char(glyphName) + '(expr moveSizeOfH, moveSizeOfV) =\n') #!!!!!!!!!!!!!!!
        fp.write('def ' + _num2char(
            glyphName) + '(expr Width, Height, moveSizeOfH, moveSizeOfV, penWidthRate, penHeightRate, curveRate, serifRate, unfillRate, isUnfill) =\n')

        # Get UFO data by xml parser
        UNDEFINED = 9999
        leftP = [[UNDEFINED for col in range(2)] for row in range(totalNum)]
        rightP = [[UNDEFINED for col in range(2)] for row in range(totalNum)]
        diffP = [[0 for col in range(2)] for row in range(totalNum)]
        dependLX = [0 for i in range(totalNum)]
        dependRX = [0 for i in range(totalNum)]
        dependLY = [0 for i in range(totalNum)]
        dependRY = [0 for i in range(totalNum)]
        penWidth = [-1 for i in range(totalNum)]
        penHeight = [-1 for i in range(totalNum)]
        cp = []
        cpX = []
        cpY = []
        type = []
        pointOrder = []
        pointCnt = 0
        cpCnt = 0
        existRound = False

        ########################################################################################
        # Get point's tag information
        node = xmlData.getElementsByTagName('point')

        rpoints = []
        for rcontour in rglyph:
            rpoints += rcontour.points
        rpointsattr = []
        for rpoint in rpoints:
            rpointsattr.append(name2dict(rpoint.name))

        for i in range(len(node)):
            # if have a penPair attribute
            try:
                # name = node[i].attributes['penPair'].value
                name = rpointsattr[i]['penPair']
                # Get pointNumber and Store point order
                pointNumber = int(name[1:-1])
                if name.find('l') != -1:
                    idx = pointNumber * 2 - 1
                elif name.find('r') != -1:
                    idx = pointNumber * 2
                else:
                    print('Error : penPair attribute have a incorrect format value (' + name + ')')
                    return

                pointOrder.append(idx)

                # Store basic information of point having a penPair attribute
                # print("length:", len(points), ", idx:", idx)
                points[idx].name = name
                points[idx].type = node[i].attributes['type'].value
                points[idx].x = str(float(node[i].attributes['x'].value) / fontWidth)
                points[idx].y = str(float(node[i].attributes['y'].value) / fontWidth)
                points[idx].idx = pointCnt
                pointCnt = pointCnt + 1

                # If point have a special attributes, stroe it
                try:
                    # points[idx].dependX = node[i].attributes['dependX'].value
                    points[idx].dependX = rpointsattr[i]['dependX']
                except:
                    notting = 0

                try:
                    # points[idx].dependY = node[i].attributes['dependY'].value
                    points[idx].dependY = rpointsattr[i]['dependY']
                except:
                    notting = 0

                try:
                    # points[idx].startP = node[i].attributes['innerType'].value
                    points[idx].startP = rpointsattr[i]['innerType']
                    if len(pointOrder) > 1:
                        points[pointOrder[-2]].endP = 'end'
                    firstIdx = idx
                except:
                    notting = 0

                try:
                    # points[idx].serif = node[i].attributes['serif'].value
                    points[idx].serif = rpointsattr[i]['serif']
                except:
                    notting = 0

                try:
                    # points[idx].roundA = node[i].attributes['round'].value  # add round attribute
                    points[idx].roundA = rpointsattr[i]['round']
                    existRound = True
                except:
                    notting = 0

                try:
                    # points[idx].char = node[i].attribute['char'].value
                    points[idx].char = rpointsattr[i]['char']
                except:
                    notting = 0

                try:
                    # points[idx].sound = node[i].attribute['sound'].value
                    points[idx].sound = rpointsattr[i]['sound']
                except:
                    notting = 0

                try:
                    # points[idx].formType = node[i].attribute['formType'].value
                    points[idx].formType = rpointsattr[i]['formType']
                except:
                    notting = 0

                try:
                    # points[idx].double = node[i].attribute['double'].value
                    points[idx].double = rpointsattr[i]['double']
                except:
                    notting = 0

                try:
                    # points[idx].customer = node[i].attributes['customer'].value
                    points[idx].customer = rpointsattr[i]['customer']
                except:
                    notting = 0

            # if not have penPair attribute, it is control point
            except:
                # print(glyphName)
                idx = pointOrder[-1]
                xValue = node[i].attributes['x'].value
                yValue = node[i].attributes['y'].value
                points[idx].controlPoints.append([xValue, yValue])

        points[pointOrder[-1]].endP = 'end'

        for rcontour in rglyph:
            for rpoint in rcontour.points:
                rpoint.x /= fontWidth
                rpoint.y /= fontWidth

        ##############################################################################
        # Set pen's paramter
        siotcontours = []
        jiotcontours = []
        siotnums = {'first': ['9', '10'], 'final': ['3', '12', '18', '19', '20']}
        jiotnums = {'first': ['12', '13', '14'], 'final': ['5', '22', '23']}
        firstattr = Attribute(rglyph[0].points[0])
        if firstattr.get_attr('sound') == 'first':
            if firstattr.get_attr('char') in siotnums['first']:
                for rcontour in rglyph:
                    siotcontours.append(rcontour)
            elif firstattr.get_attr('char') in jiotnums['first']:
                for rcontour in rglyph:
                    if rcontour.bounds[1] == rglyph.bounds[1]:
                        jiotcontours.append(rcontour)
        elif firstattr.get_attr('sound') == 'final':
            if firstattr.get_attr('char') in siotnums['final']:
                if firstattr.get_attr('double') is None:
                    for rcontour in rglyph:
                        siotcontours.append(rcontour)
                else:
                    for rcontour in rglyph:
                        attr = Attribute(rcontour.points[0])
                        if attr.get_attr('double') == 'right':
                            siotcontours.append(rcontour)
            elif firstattr.get_attr('char') in jiotnums['final']:
                if firstattr.get_attr('double') is None:
                    for rcontour in rglyph:
                        if rcontour.bounds[1] == rglyph.bounds[1]:
                            jiotcontours.append(rcontour)
                else:
                    for rcontour in rglyph:
                        attr = Attribute(rcontour.points[0])
                        if attr.get_attr('double') == 'right' and rcontour.bounds[1] == rglyph.bounds[1]:
                            jiotcontours.append(rcontour)

        fp.write("\n% pen parameter \n")
        # for i in range(1, int(totalNum / 2)):
        #     l = i * 2 - 1
        #     r = i * 2
        #
        #     if points[l].name == "" or points[r].name == "":
        #         continue
        #     elif str(i) in siotpairdict.keys():
        #         continue
        #
        #     penWidth[i] = float(points[l].x) - float(points[r].x)
        #     penHeight[i] = float(points[l].y) - float(points[r].y)
        #
        #     # *** Changed *** #
        #     fp.write("penWidth_" + str(i) + " := (((penWidthRate - 1) * "
        #         + _float2str(penWidth[i]) + ") / 2) * Width;\n")
        #     # *** Changed *** #
        #     fp.write("penHeight_" + str(i) + " := (((penHeightRate - 1) * "
        #         + _float2str(penHeight[i]) + ") / 2) * Height;\n")

        siotpairdict = getpairdict(siotcontours)
        siotorder = sorted(siotpairdict, key=lambda pair: siotpairdict[pair]['l'].x if siotpairdict[pair]['l'].y > siotpairdict[pair]['r'].y else siotpairdict[pair]['r'].x)
        jiotpairdict = getpairdict(jiotcontours)
        jiotorder = sorted(jiotpairdict, key=lambda pair: jiotpairdict[pair]['l'].x if jiotpairdict[pair]['l'].y > jiotpairdict[pair]['r'].y else jiotpairdict[pair]['r'].x)
        pairdict = getpairdict(rglyph)
        penform = 'pen{HW}_{num}{opt} := (((pen{HWR}Rate - 1) * {diff:0.3f}) / 2) * {HW};\n'
        for pair in pairdict.keys():
            penpair = pairdict[pair]

            if len(penpair) != 2:
                continue

            penWidth[int(pair)] = float(penpair['l'].x) - float(penpair['r'].x)
            penHeight[int(pair)] = float(penpair['l'].y) - float(penpair['r'].y)

            # bounds = penpair['l'].contour.bounds
            if pair in siotpairdict.keys():
                if pair == siotorder[0]:
                    fp.write(penform.format(HW='Width', num=pair, HWR='Height', diff=penWidth[int(pair)], opt=''))
                    fp.write(penform.format(HW='Height', num=pair, HWR='Height', diff=penHeight[int(pair)], opt=''))
                elif pair == siotorder[-1]:
                    fp.write(penform.format(HW='Width', num=pair, HWR='Width', diff=penWidth[int(pair)], opt=''))
                    fp.write(penform.format(HW='Height', num=pair, HWR='Width', diff=penHeight[int(pair)], opt=''))
                else:
                    fp.write(penform.format(HW='Width', num=pair, HWR='Height', diff=penWidth[int(pair)], opt='_h'))
                    fp.write(penform.format(HW='Height', num=pair, HWR='Height', diff=penHeight[int(pair)], opt='_h'))
                    fp.write(penform.format(HW='Width', num=pair, HWR='Width', diff=penWidth[int(pair)], opt='_w'))
                    fp.write(penform.format(HW='Height', num=pair, HWR='Width', diff=penHeight[int(pair)], opt='_w'))
            elif pair in jiotpairdict.keys():
                if jiotorder.index(pair) in [0, 1, 4]:
                    fp.write(penform.format(HW='Width', num=pair, HWR='Height', diff=penWidth[int(pair)], opt=''))
                    fp.write(penform.format(HW='Height', num=pair, HWR='Height', diff=penHeight[int(pair)], opt=''))
                elif jiotorder.index(pair) in [2, 5, 6] or (jiotorder.index(pair) == 3 and jiotorder[-1] == pair):
                    fp.write(penform.format(HW='Width', num=pair, HWR='Width', diff=penWidth[int(pair)], opt=''))
                    fp.write(penform.format(HW='Height', num=pair, HWR='Width', diff=penHeight[int(pair)], opt=''))
                else:
                    fp.write(penform.format(HW='Width', num=pair, HWR='Height', diff=penWidth[int(pair)], opt='_h'))
                    fp.write(penform.format(HW='Height', num=pair, HWR='Height', diff=penHeight[int(pair)], opt='_h'))
                    fp.write(penform.format(HW='Width', num=pair, HWR='Width', diff=penWidth[int(pair)], opt='_w'))
                    fp.write(penform.format(HW='Height', num=pair, HWR='Width', diff=penHeight[int(pair)], opt='_w'))
            else:
                fp.write(penform.format(HW='Width', num=pair, HWR='Width', diff=penWidth[int(pair)], opt=''))
                fp.write(penform.format(HW='Height', num=pair, HWR='Height', diff=penHeight[int(pair)], opt=''))

        ##############################################################################
        # L, R points
        fp.write("\n% point coordinates \n")
        for i in range(len(pointOrder)):
            idx = pointOrder[i]
            name = points[idx].name[1:]

            if len(siotorder) > 0 and name[: -1] in siotorder[1: -1]:
                continue
            elif len(jiotorder) > 0 and name[: -1] in jiotorder[1: -1]:
                continue

            if name.find("l") != -1:
                op = "+"
            else:
                op = "-"

            fp.write("x" + name + " := (" + _float2str(float(points[idx].x)))

            if points[idx].customer != "":
                fp.write(" + " + points[idx].customer)

            fp.write(" + " + "moveSizeOfH) * " + "Width ")
            if points[idx].dependX != "":
                dependXValue = points[idx].dependX
                if dependXValue.find("l") != -1:
                    fp.write("+ penWidth_" + dependXValue[1:-1])
                else:
                    fp.write("- penWidth_" + dependXValue[1:-1])
            elif penWidth[int(name[0:-1])] != -1:
                fp.write(op + " penWidth_" + name[0:-1])
            fp.write(";\n")

            fp.write(
                "y" + name + " := (" + _float2str(float(points[idx].y)) + " + " + "moveSizeOfV) * " + "Height ")
            if points[idx].dependY != "":
                dependYValue = points[idx].dependY
                if dependYValue.find("l") != -1:
                    fp.write("+ penHeight_" + dependYValue[1:-1])
                else:
                    fp.write("- penHeight_" + dependYValue[1:-1])
            elif penHeight[int(name[0:-1])] != -1:
                fp.write(op + " penHeight_" + name[0:-1])
            fp.write(";\n")

        pointform = '{xy}{pair}{opt1}{opt2}{lr} := ({coord:0.3f} + moveSizeOf{hv}) * {hw} {op} pen{hw}_{pair}{opt1};\n'
        for pair in pairdict.keys():
            penpair = pairdict[pair]

            if len(siotorder) > 0 and pair in siotorder[1: -1]:
                pass
            elif len(jiotorder) > 0 and pair in jiotorder[1: -1]:
                pass
            else:
                continue

            if pair in jiotorder[1: -1] and jiotorder.index(pair) % 3 != 0:
                for lr in penpair.keys():
                    if lr == 'l':
                        op = '+'
                    else:
                        op = '-'
                    fp.write(
                        pointform.format(xy='x', pair=pair, lr=lr, coord=penpair[lr].x, hv='H', hw='Width', op=op,
                                         opt1='', opt2='_'))
                    fp.write(
                        pointform.format(xy='y', pair=pair, lr=lr, coord=penpair[lr].y, hv='V', hw='Height', op=op,
                                         opt1='', opt2='_'))
            else:
                for lr in penpair.keys():
                    if lr == 'l':
                        op = '+'
                    else:
                        op = '-'
                    fp.write(
                        pointform.format(xy='x', pair=pair, lr=lr, coord=penpair[lr].x, hv='H', hw='Width', op=op,
                                         opt1='_h', opt2=''))
                    fp.write(
                        pointform.format(xy='y', pair=pair, lr=lr, coord=penpair[lr].y, hv='V', hw='Height', op=op,
                                         opt1='_h', opt2=''))
                    fp.write(
                        pointform.format(xy='x', pair=pair, lr=lr, coord=penpair[lr].x, hv='H', hw='Width', op=op,
                                         opt1='_w', opt2=''))
                    fp.write(
                        pointform.format(xy='y', pair=pair, lr=lr, coord=penpair[lr].y, hv='V', hw='Height', op=op,
                                         opt1='_w', opt2=''))

        lineform = 'z{start} -- 2[z{start}, z{end}]'
        vlineform = '0.5[z{start}l, z{start}r] -- 0.5[z{end}l, z{end}r]'
        insecform = '{xy}part (({lineform1}) intersectionpoint ({lineform2}))'
        insecpointform = '{xy}{pair}{lr} := {insecform};\n'
        ifinsecform = 'if {insecform} > ypart (0.5[z{start}l, z{start}r]):\n'
        ifinsecform += '\t{vinsecpointformx}\t{vinsecpointformy}'
        ifinsecform += 'else:\n\t{insecpointformx}\t{insecpointformy}fi\n'

        for i in range(1, len(siotorder) - 1):
            pairlist = siotorder[i - 1: i + 2]
            upside = ['l' if pairdict[pair]['l'].y > pairdict[pair]['r'].y else 'r' for pair in pairlist]
            downside = ['l' if side == 'r' else 'r' for side in upside]

            if i % 2 != 0:
                opt = ['_h', '_w']
            else:
                opt = ['_w', '_h']

            insecpoints = []
            for side in [upside, downside]:
                start = [pairlist[0] + (opt[0] if pairlist[0] != siotorder[0] else '') + side[0],
                         pairlist[2] + (opt[1] if pairlist[2] != siotorder[-1] else '') + side[2]]
                end = [pairlist[1] + opt[0] + side[1], pairlist[1] + opt[1] + side[1]]
                line = [lineform.format(start=start[num], end=end[num]) for num in range(len(start))]
                for xy in ['x', 'y']:
                    insec = insecform.format(xy=xy, lineform1=line[0], lineform2=line[1])
                    insecpoint = insecpointform.format(xy=xy, pair=pairlist[1], lr=side[1], insecform=insec)
                    insecpoints.append(insecpoint)

            for insecpoint in insecpoints:
                fp.write(insecpoint)

        for i in range(1, len(jiotorder) - 1):
            curpair = jiotorder[i]
            if i % 3 == 1:
                pairlist = jiotorder[i - 1: i + 3]
            elif i % 3 == 2:
                pairlist = jiotorder[i - 2: i + 2]
            else:
                pairlist = jiotorder[i - 1: i + 2]

            upside = ['l' if pairdict[pair]['l'].y > pairdict[pair]['r'].y else 'r' for pair in pairlist]
            downside = ['l' if side == 'r' else 'r' for side in upside]

            if i % 3 != 0:
                for rcontour in rglyph:
                    point = jiotpairdict[pairlist[1]][upside[1]]
                    if rcontour.pointInside((point.x, point.y)):
                        hatcontour = rcontour
                hatpairdict = getpairdict([hatcontour])
                hatpairlist = list(hatpairdict.keys())

                opt = []
                for pair in pairlist:
                    if pair in [jiotorder[0], jiotorder[-1]]:
                        opt.append('')
                    elif jiotorder.index(pair) % 3 in [1, 2]:
                        opt.append('_')
                    else:
                        if pair == pairlist[0]:
                            opt.append('_h')
                        elif pair == pairlist[-1]:
                            opt.append('_w')

                start = [pairlist[0] + opt[0] + upside[0], pairlist[3] + opt[3] + upside[3]]
                end = [pairlist[1] + opt[1] + upside[1], pairlist[2] + opt[2] + upside[2]]
                line = [lineform.format(start=start[num], end=end[num]) for num in range(len(start))]
                vline = vlineform.format(start=hatpairlist[0], end=hatpairlist[1])
                insec = {}
                vinsec = {}
                insecpoint = {}
                vinsecpoint = {}
                for xy in ['x', 'y']:
                    insec[xy] = insecform.format(xy=xy, lineform1=line[0], lineform2=line[1])
                    vinsec[xy] = insecform.format(xy=xy, lineform1=vline, lineform2=line[i % 3 - 1])
                    insecpoint[xy] = insecpointform.format(xy=xy, pair=curpair, lr=upside[pairlist.index(curpair)],
                                                           insecform=insec[xy])
                    vinsecpoint[xy] = insecpointform.format(xy=xy, pair=curpair, lr=upside[pairlist.index(curpair)],
                                                            insecform=vinsec[xy])
                ifinsec = ifinsecform.format(insecform=insec['y'], start=hatpairlist[0],
                                             vinsecpointformx=vinsecpoint['x'], vinsecpointformy=vinsecpoint['y'],
                                             insecpointformx=insecpoint['x'], insecpointformy=insecpoint['y'])
                fp.write(ifinsec)

                start = [pairlist[0] + opt[0] + downside[0], pairlist[3] + opt[3] + downside[3]]
                end = [pairlist[1] + opt[1] + downside[1], pairlist[2] + opt[2] + downside[2]]
                line = [lineform.format(start=start[num], end=end[num]) for num in range(len(start))]
                downinsecpoints = []
                for xy in ['x', 'y']:
                    insec = insecform.format(xy=xy, lineform1=line[0], lineform2=line[1])
                    insecpoint = insecpointform.format(xy=xy, pair=curpair, lr=downside[pairlist.index(curpair)],
                                                       insecform=insec)
                    downinsecpoints.append(insecpoint)
                for insecpoint in downinsecpoints:
                    fp.write(insecpoint)
            else:
                opt = ['_w', '_h']

                insecpoints = []
                for side in [upside, downside]:
                    start = [pairlist[0] + '_' + side[0], pairlist[2] + '_' + side[2]]
                    end = [pairlist[1] + opt[0] + side[1], pairlist[1] + opt[1] + side[1]]
                    line = [lineform.format(start=start[num], end=end[num]) for num in range(len(start))]
                    for xy in ['x', 'y']:
                        insec = insecform.format(xy=xy, lineform1=line[0], lineform2=line[1])
                        insecpoint = insecpointform.format(xy=xy, pair=pairlist[1], lr=side[1], insecform=insec)
                        insecpoints.append(insecpoint)

                for insecpoint in insecpoints:
                    fp.write(insecpoint)

            """
        ##############################################################################
        # Set dependency
        fp.write("\n% dependency\n")
        for i in range(len(pointOrder)):
            idx = pointOrder[i]
            name = points[idx].name[1:]

            if points[idx].dependX != "":
                dependIdx = points[idx].dependX[1:-1]
                if points[idx].dependX.find("r") > -1 :
                    fp.write("x" + name + " := x" + name + " - penWidth_" + dependIdx + ";\n")
                else:
                    fp.write("x" + name + " := x" + name + " + penWidth_" + dependIdx + ";\n")
            if points[idx].dependY != "":
                dependIdx = points[idx].dependY[1:-1]
                if points[idx].dependY.find("r") > -1 :
                    fp.write("y" + name + " := y" + name + " - penHeight_" + dependIdx + ";\n")
                else:
                    fp.write("y" + name + " := y" + name + " + penHeight_" + dependIdx + ";\n")
        """
        ###############################################################################
        fp.write("\n% control point\n")
        circlepoints = []
        if (points[pointOrder[0]].sound == 'first' and (
                points[pointOrder[0]].char == '11' or (points[pointOrder[0]].char == '18'))) or (
                points[pointOrder[0]].sound == 'final' and (
                points[pointOrder[0]].char == '21' or (points[pointOrder[0]].char == '27'))):
            for i in range(len(pointOrder)):
                curIdx = pointOrder[i]
                if points[curIdx].startP != '':
                    firstOI = i
                    iscurve = 1
                    isright = 1
                    isleft = 1

                if points[curIdx].type != 'curve':
                    iscurve *= 0
                if points[curIdx].name[-1] == 'l':
                    isright *= 0
                else:
                    isleft *= 0

                if points[curIdx].endP != '':
                    if iscurve == 1 and (isright != isleft):
                        circlepoints += range(firstOI, i + 1)

        for i in range(0, len(pointOrder)):
            if i in circlepoints:
                continue

            if points[pointOrder[i]].startP != "":
                firstIdx = pointOrder[i]

            if i == len(pointOrder) - 1 or points[pointOrder[i + 1]].startP != "":
                curIdx = pointOrder[i]
                nextIdx = firstIdx
            else:
                curIdx = pointOrder[i]
                nextIdx = pointOrder[i + 1]

            if points[nextIdx].name == "" or points[nextIdx].type == "line":
                continue

            name = points[curIdx].name[1:-1]
            nextName = points[nextIdx].name[1:-1]
            way = points[curIdx].name[-1]

            if points[curIdx].name.find("l") != -1:
                curOp = "+"
            else:
                curOp = "-"

            if points[nextIdx].name.find("l") != -1:
                nextOp = "+"
            else:
                nextOp = "-"

            curPenWidthIdx = int(name)
            curPenHeightIdx = int(name)
            nextPenWidthIdx = int(nextName)
            nextPenHeightIdx = int(nextName)

            dependXValue = points[curIdx].dependX
            if dependXValue != "":
                if dependXValue.find("l") != -1:
                    curPenW = "+ penWidth_" + dependXValue[1:-1]
                else:
                    curPenW = "- penWidth_" + dependXValue[1:-1]
                curPenWidthIdx = int(dependXValue[1:-1])
            elif penWidth[int(name)] != -1:
                curPenW = curOp + " penWidth_" + name
            else:
                curPenW = ""

            dependYValue = points[curIdx].dependY
            if dependYValue != "":
                if dependYValue.find("l") != -1:
                    curPenH = "+ penHeight_" + dependYValue[1:-1]
                else:
                    curPenH = "- penHeight_" + dependYValue[1:-1]
                curPenHeightIdx = int(dependYValue[1:-1])
            elif penHeight[int(name)] != -1:
                curPenH = curOp + " penHeight_" + name
            else:
                curPenH = ""

            dependXValue = points[nextIdx].dependX
            if dependXValue != "":
                if dependXValue.find("l") != -1:
                    nextPenW = "+ penWidth_" + dependXValue[1:-1]
                else:
                    nextPenW = "- penWidth_" + dependXValue[1:-1]
                nextPenWidthIdx = int(dependXValue[1:-1])
            elif penWidth[int(nextName)] != -1:
                nextPenW = nextOp + " penWidth_" + nextName
            else:
                nextPenW = ""

            dependYValue = points[nextIdx].dependY
            if dependYValue != "":
                if dependYValue.find("l") != -1:
                    nextPenH = "+ penHeight_" + dependYValue[1:-1]
                else:
                    nextPenH = "- penHeight_" + dependYValue[1:-1]
                nextPenHeightIdx = int(dependYValue[1:-1])
            elif penHeight[int(nextName)] != -1:
                nextPenH = nextOp + " penHeight_" + nextName
            else:
                nextPenH = ""

            if points[curIdx].customer != "":
                curCustomer = points[curIdx].customer
            else:
                curCustomer = ""

            if points[nextIdx].customer != "":
                nextCustomer = points[nextIdx].customer
            else:
                nextCustomer = ""

            pointName = points[curIdx].name[1:]
            # *** Changed float -> _float2str() *** #
            if points[nextIdx].type == "curve":
                fp.write("x" + pointName + "1 := (" + _float2str(float(points[curIdx].controlPoints[0][
                                                                                  0]) / fontWidth) + " + " + curCustomer + " + moveSizeOfH) * Width " + curPenW + ";\n")
                fp.write("y" + pointName + "1 := (" + _float2str(float(
                    points[curIdx].controlPoints[0][1]) / fontWidth) + " + moveSizeOfV) * Height " + curPenH + ";\n")
                #   fp.write("x" + pointName + "1 := x" + pointName + "1 - (1 - curveRate)*(" + "x" + pointName + "1 - x" + pointName + "); ")
                #   fp.write("y" + pointName + "1 := y" + pointName + "1 - (1 - curveRate)*(" + "y" + pointName + "1 - y" + pointName + ");\n")
                fp.write("x" + pointName + "2 := (" + _float2str(float(points[curIdx].controlPoints[1][
                                                                                  0]) / fontWidth) + " + " + nextCustomer + " + moveSizeOfH) * Width " + nextPenW + ";\n")
                fp.write("y" + pointName + "2 := (" + _float2str(float(
                    points[curIdx].controlPoints[1][1]) / fontWidth) + " + moveSizeOfV) * Height " + nextPenH + ";\n")
            #   fp.write("x" + pointName + "2 := x" + pointName + "2 - (1 - curveRate)*(" + "x" + pointName + "2 - x" + pointName + "); ")
            #   fp.write("y" + pointName + "2 := y" + pointName + "2 - (1 - curveRate)*(" + "y" + pointName + "2 - y" + pointName + ");\n")
            elif points[nextIdx].type == "qcurve":
                size = len(points[curIdx].controlPoints)
                for j in range(0, size):
                    if size % 2 == 1 and j == size / 2:
                        if penWidth[curPenWidthIdx] > penWidth[nextPenWidthIdx]:
                            fp.write("x" + pointName + str(j + 1) + " := (" + _float2str(float(
                                points[curIdx].controlPoints[j][
                                    0]) / fontWidth) + " + " + curCustomer + " + moveSizeOfH) * Width " + curPenW + ";\n")
                        else:
                            fp.write("x" + pointName + str(j + 1) + " := (" + _float2str(float(
                                points[curIdx].controlPoints[j][
                                    0]) / fontWidth) + " + " + nextCustomer + " + moveSizeOfH) * Width " + nextPenW + ";\n")

                        if penHeight[curPenHeightIdx] > penHeight[nextPenHeightIdx]:
                            fp.write("y" + pointName + str(j + 1) + " := (" + _float2str(float(
                                points[curIdx].controlPoints[j][
                                    1]) / fontWidth) + " + moveSizeOfV) * Height " + curPenH + ";\n")
                        else:
                            fp.write("y" + pointName + str(j + 1) + " := (" + _float2str(float(
                                points[curIdx].controlPoints[j][
                                    1]) / fontWidth) + " + moveSizeOfV) * Height " + nextPenH + ";\n")

                    elif j < size / 2:
                        fp.write("x" + pointName + str(j + 1) + " := (" + _float2str(float(
                            points[curIdx].controlPoints[j][
                                0]) / fontWidth) + " + " + curCustomer + " + moveSizeOfH) * Width " + curPenW + ";\n")
                        fp.write("y" + pointName + str(j + 1) + " := (" + _float2str(float(
                            points[curIdx].controlPoints[j][
                                1]) / fontWidth) + " + moveSizeOfV) * Height " + curPenH + ";\n")
                    else:
                        fp.write("x" + pointName + str(j + 1) + " := (" + _float2str(float(
                            points[curIdx].controlPoints[j][
                                0]) / fontWidth) + " + " + nextCustomer + " + moveSizeOfH) * Width " + nextPenW + ";\n")
                        fp.write("y" + pointName + str(j + 1) + " := (" + _float2str(float(
                            points[curIdx].controlPoints[j][
                                1]) / fontWidth) + " + moveSizeOfV) * Height " + nextPenH + ";\n")

            #       fp.write("x" + pointName + str(j+1) + " := x" + pointName + str(j+1) + " - (1 - curveRate) * (" + "x" + pointName + str(j+1) + " - x" + pointName + "); ")
            #       fp.write("y" + pointName + str(j+1) + " := y" + pointName + str(j+1) + " - (1 - curveRate) * (" + "y" + pointName + str(j+1) + " - y" + pointName + ");\n")

        if len(circlepoints) != 0:
            raidusform = '(({anchor} {op} {anchorpen} - ({revname} {op} {revpen})) / 2)'
            bcpform = '{bcpname}{num} := {anchor} * {coordrate} {op} {pen} / {raidus} * (1 - {coordrate}) * {anchor};\n'
            for rcontour in rglyph:
                if len(rcontour.points) != len(rcontour) * 3:
                    continue

                cboundx = [rcontour.bounds[0], rcontour.bounds[2]]
                cboundy = [rcontour.bounds[1], rcontour.bounds[3]]

                for cursegidx in range(len(rcontour)):
                    curseg = rcontour[cursegidx]
                    preseg = rcontour[cursegidx - 1]
                    revsegs = [rcontour[cursegidx - 1 - len(rcontour) // 2], rcontour[cursegidx - len(rcontour) // 2]]

                    curpoint = curseg.onCurve
                    prepoint = preseg.onCurve
                    revpoints = [seg.onCurve for seg in revsegs]
                    bcpoint = curseg.offCurve

                    curattr = Attribute(curpoint)
                    preattr = Attribute(prepoint)
                    revattrs = [Attribute(revpoint) for revpoint in revpoints]

                    revnames = [revattr.get_attr('penPair')[1:] for revattr in revattrs]
                    anchor = [preattr.get_attr('penPair')[1:], curattr.get_attr('penPair')[1:]]
                    bcpname = anchor[0]
                    coordratex = ['%0.3f / %0.3f' % (bcpoint[0].x, prepoint.x),
                                  '%0.3f / %0.3f' % (bcpoint[1].x, curpoint.x)]
                    coordratey = ['%0.3f / %0.3f' % (bcpoint[0].y, prepoint.y),
                                  '%0.3f / %0.3f' % (bcpoint[1].y, curpoint.y)]
                    penx = ['penHeight_%s' % (x[:-1]) for x in anchor]
                    peny = ['penWidth_%s' % (x[:-1]) for x in anchor]

                    raidus = []
                    op = '-' if bcpname[-1] == 'l' else '+'
                    if prepoint.x in cboundx:
                        pen = 'penWidth_'
                        raidus.append(raidusform.format(anchor='x' + anchor[0], anchorpen=pen + anchor[0][:-1],
                                                        revname='x' + revnames[0], revpen=pen + revnames[0][:-1], op=op))
                    elif prepoint.y in cboundy:
                        pen = 'penHeight_'
                        raidus.append(raidusform.format(anchor='y' + anchor[0], anchorpen=pen + anchor[0][:-1],
                                                        revname='y' + revnames[0], revpen=pen + revnames[0][:-1], op=op))
                    if curpoint.x in cboundx:
                        pen = 'penWidth_'
                        raidus.append(raidusform.format(anchor='x' + anchor[1], anchorpen=pen + anchor[1][:-1],
                                                        revname='x' + revnames[1], revpen=pen + revnames[1][:-1], op=op))
                    elif curpoint.y in cboundy:
                        pen = 'penHeight_'
                        raidus.append(raidusform.format(anchor='y' + anchor[1], anchorpen=pen + anchor[1][:-1],
                                                        revname='y' + revnames[1], revpen=pen + revnames[1][:-1], op=op))

                    for num in range(2):
                        fp.write(bcpform.format(bcpname='x' + bcpname, num=num + 1, anchor='x' + anchor[num],
                                                coordrate=coordratex[num], pen=penx[num], raidus=raidus[num], op=op))
                        fp.write(bcpform.format(bcpname='y' + bcpname, num=num + 1, anchor='y' + anchor[num],
                                                coordrate=coordratey[num], pen=peny[num], raidus=raidus[num], op=op))

        #####################################################################################
        # round point
        if existRound:
            fp.write('\n% round point\n')
            fp.write('if curveRate > 0.0:\n')

            numPoints = len(pointOrder)
            startIdx = 0
            endIdx = 0
            for i in range(numPoints):
                curIdx = pointOrder[i]
                curPoint = points[curIdx]

                if curPoint.startP != '':
                    startIdx = curIdx
                    for j in range(i + 1, numPoints):
                        if points[pointOrder[j]].endP != '':
                            endIdx = pointOrder[j]
                            break

                if curPoint.roundA == "":
                    continue

                preIdx = pointOrder[(i - 1 + numPoints) % numPoints]
                nextIdx = pointOrder[(i + 1) % numPoints]

                if curIdx == startIdx:
                    preIdx = endIdx
                elif curIdx == endIdx:
                    nextIdx = startIdx

                prePoint = points[preIdx]
                nextPoint = points[nextIdx]

                if curIdx % 2 == 0:
                    pairIdx = curIdx - 1
                    pairPoint = points[pairIdx]
                else:
                    pairIdx = curIdx + 1
                    pairPoint = points[pairIdx]

                dists = []
                dists.append(float(prePoint.x) - float(curPoint.x))
                dists.append(float(prePoint.y) - float(curPoint.y))
                dists.append(float(nextPoint.x) - float(curPoint.x))
                dists.append(float(nextPoint.y) - float(curPoint.y))

                op = []
                zeroDist = []
                for j in range(len(dists)):
                    if dists[j] < 0:
                        op.append('-')
                    else:
                        op.append('+')
                    zeroDist.append(math.isclose(dists[j], 0))

                # if float(prePoint.x) - float(curPoint.x) < 0:
                #   op.append('-')
                # else:
                #   op.append('+')
                # if float(prePoint.y) - float(curPoint.y) < 0:
                #   op.append('-')
                # else:
                #   op.append('+')
                # if float(nextPoint.x) - float(curPoint.x) < 0:
                #   op.append('-')
                # else:
                #   op.append('+')
                # if float(nextPoint.y) - float(curPoint.y) < 0:
                #   op.append('-')
                # else:
                #   op.append('+')

                pointName = curPoint.name[1:]
                nameForm = '%s' + pointName[:-1] + '_R%d' + pointName[-1] + ' := %s' + pointName
                distForm1 = 'abs(%s' + pointName[:-1] + 'l - %s' + pointName[:-1] + 'r)'
                distForm2 = 'max(' + distForm1 % ('x', 'x') + ', ' + distForm1 % ('y', 'y') + ")"
                curveRate = '/ 2 * curveRate'
                bcpRate = '* 0.45'
                distParam = [None for i in range(4)]
                roundP = []
                roundBcp = []

                if pairIdx == preIdx:
                    distParam[0] = distParam[3] = ('x', 'x')
                    distParam[1] = distParam[2] = ('y', 'y')
                    for j in range(4):
                        roundP.append(op[j] + ' ' + distForm1 % distParam[j] + ' ' + curveRate)
                        roundBcp.append(roundP[-1] + ' ' + bcpRate)
                elif pairIdx == nextIdx:
                    distParam[0] = distParam[3] = ('y', 'y')
                    distParam[1] = distParam[2] = ('x', 'x')
                    for j in range(4):
                        roundP.append(op[j] + ' ' + distForm1 % distParam[j] + ' ' + curveRate)
                        roundBcp.append(roundP[-1] + ' ' + bcpRate)
                else:
                    for j in range(4):
                        if zeroDist[j]:
                            roundP.append('')
                            roundBcp.append('')
                        else:
                            roundP.append(op[j] + ' ' + distForm2 + ' ' + curveRate)
                            roundBcp.append(roundP[-1] + ' ' + bcpRate)

                fp.write(
                    '\t' + nameForm % ('x', 0, 'x') + ' ' + roundP[0] + ';\n\t' + nameForm % ('y', 0, 'y') + roundP[
                        1] + ';\n')
                fp.write(
                    '\t' + nameForm % ('x', 1, 'x') + ' ' + roundBcp[0] + ';\n\t' + nameForm % ('y', 1, 'y') + roundBcp[
                        1] + ';\n')
                fp.write(
                    '\t' + nameForm % ('x', 2, 'x') + ' ' + roundBcp[2] + ';\n\t' + nameForm % ('y', 2, 'y') + roundBcp[
                        3] + ';\n')
                fp.write(
                    '\t' + nameForm % ('x', 3, 'x') + ' ' + roundP[2] + ';\n\t' + nameForm % ('y', 3, 'y') + roundP[
                        3] + ';\n')

            fp.write('fi\n')

        #####################################################################################

        # *** Changed ***
        # add round point path
        #####################################################################################################################################
        # Get draw

        fp.write("\n% Get draw \n");
        fp.write("if isUnfill:\n");
        fp.write("\tindex := 2;\n");
        fp.write("else:\n");
        fp.write("\tindex := 0;\n");
        fp.write("fi\n");

        source = ""
        sourceR = ""
        dash = ""
        startIdx = 0
        serifList = []
        for i in range(0, len(pointOrder)):
            # source += '\t'
            # sourceR += '\t'

            idx = pointOrder[i]

            if i + 1 != len(pointOrder) and points[pointOrder[i + 1]].startP == "":
                nextIdx = pointOrder[i + 1]
            else:
                nextIdx = startIdx

            if idx % 2 == 0:
                pairIdx = idx - 1
            else:
                pairIdx = idx + 1

            if points[idx].startP != "":
                startIdx = idx
                if points[idx].startP == "fill":
                    source = 'if isUnfill:\n\tunfill\nelse:\n\tfill\nfi\n'
                    sourceR = 'if isUnfill:\n\tunfill\nelse:\n\tfill\nfi\n'
                else:
                    source = 'if isUnfill:\n\tfill\nelse:\n\tunfill\nfi\n'
                    sourceR = 'if isUnfill:\n\tfill\nelse:\n\tunfill\nfi\n'
            # else:
            #   source = ""

            # source += points[pointOrder[i]].name
            dash = " .. "

            if points[idx].roundA != '':
                if points[idx].serif == '1' or points[idx].serif == '2':
                    serifList.append(idx)
                    sourceR += 'if serifRate > 0.0:\n'
                    sourceR += '\t' + points[idx].name + '\n'
                    sourceR += 'else:\n'
                    sourceR += '\t' + points[idx].name[:-1] + '_R0' + points[idx].name[-1] + ' .. controls (' + points[
                                                                                                                    idx].name[
                                                                                                                :-1] + '_R1' + \
                               points[idx].name[-1] + ') and (' + points[idx].name[:-1] + '_R2' + points[idx].name[
                                   -1] + ') .. \n'
                    sourceR += '\t' + points[idx].name[:-1] + '_R3' + points[idx].name[-1] + '\n'
                    sourceR += 'fi\n'
                    source += points[idx].name
                elif points[pairIdx].serif == '1' or points[pairIdx].serif == '2':
                    sourceR += 'if serifRate > 0.0:\n'
                    sourceR += '\tz%d_R0r .. controls (z%d_R1r) and (z%d_R2r) ..\n\tz%d_R3r --\n' % (
                    int(points[pairIdx].serif) * 10 + 141, int(points[pairIdx].serif) * 10 + 141,
                    int(points[pairIdx].serif) * 10 + 141, int(points[pairIdx].serif) * 10 + 141)
                    sourceR += '\tz%d_R0r .. controls (z%d_R1r) and (z%d_R2r) ..\n\tz%d_R3r --\n' % (
                    int(points[pairIdx].serif) * 10 + 142, int(points[pairIdx].serif) * 10 + 142,
                    int(points[pairIdx].serif) * 10 + 142, int(points[pairIdx].serif) * 10 + 142)
                    sourceR += '\tz%d_R0l .. controls (z%d_R1l) and (z%d_R2l) ..\n\tz%d_R3l\n' % (
                    int(points[pairIdx].serif) * 10 + 142, int(points[pairIdx].serif) * 10 + 142,
                    int(points[pairIdx].serif) * 10 + 142, int(points[pairIdx].serif) * 10 + 142)
                    sourceR += 'else:\n'
                    sourceR += '\t' + points[idx].name[:-1] + '_R0' + points[idx].name[-1] + ' .. controls (' + points[
                                                                                                                    idx].name[
                                                                                                                :-1] + '_R1' + \
                               points[idx].name[-1] + ') and (' + points[idx].name[:-1] + '_R2' + points[idx].name[
                                   -1] + ') .. \n'
                    sourceR += '\t' + points[idx].name[:-1] + '_R3' + points[idx].name[-1] + '\n'
                    sourceR += 'fi\n'
                    source += 'if serifRate > 0.0:\n\tz%dr --\n\tz%dr --\n\tz%dl\n' % (
                    int(points[pairIdx].serif) * 10 + 141, int(points[pairIdx].serif) * 10 + 142,
                    int(points[pairIdx].serif) * 10 + 142)
                    source += 'else:\n\t' + points[idx].name + '\nfi\n'
                else:
                    sourceR += points[idx].name[:-1] + '_R0' + points[idx].name[-1] + ' .. controls (' + points[
                                                                                                             idx].name[
                                                                                                         :-1] + '_R1' + \
                               points[idx].name[-1] + ') and (' + points[idx].name[:-1] + '_R2' + points[idx].name[
                                   -1] + ') .. \n'
                    sourceR += '\t' + points[idx].name[:-1] + '_R3' + points[idx].name[-1]
                    source += points[idx].name
            else:
                if points[idx].serif == '1' or points[idx].serif == '2':
                    serifList.append(idx)
                    sourceR += 'if serifRate > 0.0:\n'
                    sourceR += '\t' + points[idx].name + '\n'
                    sourceR += 'else:\n'
                    sourceR += '\t' + points[idx].name + '\n'
                    sourceR += 'fi\n'
                    source += points[idx].name
                elif points[pairIdx].serif == '1' or points[pairIdx].serif == '2':
                    sourceR += 'if serifRate > 0.0:\n'
                    sourceR += '\tz%d_R0r .. controls (z%d_R1r) and (z%d_R2r) ..\n\tz%d_R3r --\n' % (
                    int(points[pairIdx].serif) * 10 + 141, int(points[pairIdx].serif) * 10 + 141,
                    int(points[pairIdx].serif) * 10 + 141, int(points[pairIdx].serif) * 10 + 141)
                    sourceR += '\tz%d_R0r .. controls (z%d_R1r) and (z%d_R2r) ..\n\tz%d_R3r --\n' % (
                    int(points[pairIdx].serif) * 10 + 142, int(points[pairIdx].serif) * 10 + 142,
                    int(points[pairIdx].serif) * 10 + 142, int(points[pairIdx].serif) * 10 + 142)
                    sourceR += '\tz%d_R0l .. controls (z%d_R1l) and (z%d_R2l) ..\n\tz%d_R3l\n' % (
                    int(points[pairIdx].serif) * 10 + 142, int(points[pairIdx].serif) * 10 + 142,
                    int(points[pairIdx].serif) * 10 + 142, int(points[pairIdx].serif) * 10 + 142)
                    sourceR += 'else:\n'
                    sourceR += '\t' + points[idx].name + '\n'
                    sourceR += 'fi\n'
                    source += 'if serifRate > 0.0:\n\tz%dr --\n\tz%dr --\n\tz%dl\n' % (
                    int(points[pairIdx].serif) * 10 + 141, int(points[pairIdx].serif) * 10 + 142,
                    int(points[pairIdx].serif) * 10 + 142)
                    source += 'else:\n\t' + points[idx].name + '\nfi\n'
                else:
                    sourceR += points[idx].name
                    source += points[idx].name

            if points[nextIdx].type == "line":
                dash = " -- "
            elif points[nextIdx].type == "None":
                dash = " .. "
            elif points[nextIdx].type == "curve":
                dash = " .. "
                dash = dash + "controls (z" + points[idx].name[1:] + "1) and (z" + points[idx].name[1:] + "2) .. "
            elif points[nextIdx].type == "qcurve":
                dash = " .. "
                controlPoints = points[idx].controlPoints
                for j in range(0, len(controlPoints)):
                    if j == 0:
                        QP0 = points[idx].name
                    else:
                        QP0 = QP2

                    QP1 = points[idx].name + str(j + 1)
                    if j != len(controlPoints) - 1:
                        newX = "(x" + points[idx].name[1:] + str(j + 1) + " + x" + points[idx].name[1:] + str(
                            j + 2) + ") / 2"
                        newY = "(y" + points[idx].name[1:] + str(j + 1) + " + y" + points[idx].name[1:] + str(
                            j + 2) + ") / 2"
                        QP2 = "(" + newX + ", " + newY + ")"
                    else:
                        QP2 = points[nextIdx].name

                    CP1 = QP0 + " + 2 / 3 * (" + QP1 + " - " + QP0 + ")"
                    CP2 = QP2 + " + 2 / 3 * (" + QP1 + " - " + QP2 + ")"
                    dash = dash + "controls (" + CP1 + ") and (" + CP2 + ") .. "

                    if j != len(controlPoints) - 1:
                        dash = dash + QP2 + " .. "

            source = source + dash + '\n'
            sourceR = sourceR + dash + '\n'

            if points[idx].endP != "":
                source += "cycle;\n"
                sourceR += "cycle;\n"
                serifStr = ''
                if len(serifList) > 0:
                    serifStr += 'if serifRate > 0.0:\n'
                    for serifIdx in serifList:
                        serifStr += '\tserif_'
                        for serifNum in range(int(points[serifIdx].serif)):
                            serifStr += 'i'
                        serifStr += '(x' + points[serifIdx].name[1:-1] + 'l, y' + points[serifIdx].name[1:-1] + 'l, '
                        serifStr += 'x' + points[serifIdx].name[1:-1] + 'r, y' + points[serifIdx].name[1:-1] + 'r, '
                        serifStr += 'serifRate, penHeightRate / penWidthRate, curveRate, unfillRate, isUnfill);\n'
                        serifStr += '\ty' + points[serifIdx].name[1:] + ' := y%dl;\n' % (
                                    int(points[serifIdx].serif) * 10 + 142)
                    serifStr += 'fi\n'
                forStr = 'for x = 0 upto index:\n'
                if existRound:
                    forStr += '\tif curveRate > 0.0:\n'
                    forStr += '\t\t' + sourceR.replace('\n', '\n\t\t')[: -2]
                    forStr += '\telse:\n'
                    forStr += '\t\t' + source.replace('\n', '\n\t\t')[: -2]
                    forStr += '\tfi\n'
                else:
                    forStr += '\t' + source.replace('\n', '\n\t\t')[: -2]
                forStr += 'endfor\n'
                fp.write(serifStr)
                fp.write(forStr)
                serifList = []
            # fp.write(source + "\n")
        # source += '\tcycle;\n'
        # sourceR += '\tcycle;\n'

        # ifIsUnfill_unfill = "\t\tif isUnfill:\n\t\t\tunfill\n\t\telse:\n\t\t\tfill\n\t\tfi\n"
        # ifIsUnfill_fill = "\t\tif isUnfill:\n\t\t\tfill\n\t\telse:\n\t\t\tunfill\n\t\tfi\n"

        # fp.write("for x = 0 upto index:\n")
        # if existRound:
        #     fp.write('\tif curveRate > 0.0:\n')
        #     for line in sourceR.split('\n'):
        #         if line.strip().split(' ')[0] == "fill":
        #             fp.write(ifIsUnfill_unfill)
        #             fp.write('\t\t' + line.replace("fill", "") + '\n')
        #         elif line.strip().split(' ')[0] == "unfill":
        #             fp.write(ifIsUnfill_fill)
        #             fp.write('\t\t' + line.replace("unfill", "") + '\n')
        #         else:
        #             fp.write('\t\t' + line.strip() + '\n')
        #     #fp.write(sourceR)

        #     fp.write('\telse:\n')
        #     for line in source.split('\n'):
        #         if line.strip().split(' ')[0] == "fill":
        #             fp.write(ifIsUnfill_unfill)
        #             fp.write('\t\t' + line.replace("fill", "") + '\n')
        #         elif line.strip().split(' ')[0] == "unfill":
        #             fp.write(ifIsUnfill_fill)
        #             fp.write('\t\t' + line.replace("unfill", "") + '\n')
        #         else:
        #             fp.write('\t\t' + line.strip() + '\n')
        #     #fp.write(source)
        #     fp.write('\tfi\n')
        # else:
        #     fp.write(source)
        # fp.write("endfor\n")

        #########################################################################################################
        # Set serif attribute
        for i in range(0, len(points)):
            if points[i].serif == "1":  # !!!!!!!!!!!!!!!
                idx = points[i].name[1:-1]
                # fp.write('if serifRate > 0.0:\n')
                # fp.write("\tserif_i(x" + idx + "l, y" + idx + "l, x" + idx + "r, y" + idx + "r, serifRate, penHeightRate / penWidthRate, curveRate, unfillRate, isUnfill);\n")
                # fp.write('fi\n')
            elif points[i].serif == "2":
                idx = points[i].name[1:-1]
                # fp.write('if serifRate > 0.0:\n')
                # fp.write("\tserif_ii(x" + idx + "l, y" + idx + "l, x" + idx + "r, y" + idx + "r, serifRate, penHeightRate / penWidthRate, curveRate, unfillRate, isUnfill);\n")
                # fp.write('fi\n')
            # end serif test by ghj (1710A) /w glyphs.mf UFO2mf.py  xmltomf.py
            elif points[i].serif == "3":
                idx = points[i].name[1:-1]
                fp.write('if serifRate > 0.0:\n')
                fp.write("\tserif_iii(x" + idx + "l, y" + idx + "l, x" + idx + "r, y" + idx + "r, curveRate);\n")
                fp.write('fi\n')
            # end serif test by ghj (1710A) /w glyphs.mf UFO2mf.py  xmltomf.py
            elif points[i].serif == "4":
                idx = points[i].name[1:-1]
                fp.write('if serifRate > 0.0:\n')
                fp.write("\tserif_iv(x" + idx + "l, y" + idx + "l, x" + idx + "r, y" + idx + "r, curveRate);\n")
                fp.write('fi\n')
            elif points[i].serif == "5":
                idx = points[i].name[1:-1]
                fp.write('if serifRate > 0.0:\n')
                fp.write("\tserif_v(x" + idx + "l, y" + idx + "l, x" + idx + "r, y" + idx + "r, curveRate);\n")
                fp.write('fi\n')

        ##########################################################################################################
        # last

        fp.write("\n% pen labels\n");
        fp.write("penlabels(range 1 thru %d);\n" % totalNum);
        fp.write("enddef;\n\n");

        fp.close()
    return None

def get_font_width(DIR_UFO, glifs):
    width_dict = {}

    for glif in glifs:
        glif = os.path.join(DIR_UFO, glif)
        glif_data = minidom.parse(glif)
        components = glif_data.getElementsByTagName('component')

        if len(components) != 0:
            advance = glif_data.getElementsByTagName('advance')
            width = advance[0].getAttribute('width')
            if width in width_dict:
                width_dict[width] += 1
            else:
                width_dict[width] = 1

    font_width = max(width_dict.keys(), key=(lambda k: width_dict[k]))

    return float(font_width)

def getfontobject(DIR_UFO):
    return OpenFont(DIR_UFO)

def getglyphobject(glyph, rfont):
    glyph = os.path.splitext(glyph)[0]
    return rfont[glyph]

def getpairdict(rcontours):
    pairdict = {}

    for rcontour in rcontours:
        for rseg in rcontour:
            point = rseg.onCurve
            attr = Attribute(point)
            penpair = attr.get_attr('penPair')

            if not penpair[1: -1] in pairdict:
                pairdict[penpair[1: -1]] = {}
            pairdict[penpair[1: -1]][penpair[-1]] = point

    return pairdict

if __name__ == '__main__':
    ufo2mf('../../..', 'YullyeoM.ufo')