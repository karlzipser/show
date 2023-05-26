
from k4.utils.core import *

command_line_args = {
    'paths':'Desktop',
    'file_types':'jpg,jpeg,JPG,JPEG,png,PNG',
    'extent':256,
    'extent2': 512,
    'padval':0,
    'padsize':5,
    'rcratio':1.1,#1.618,
    'image_info_area_height':100,
}

 

def process_args( command_line_args ):

    gd = parse_args_to_dict( command_line_args )

    gd['paths'] = gd['paths'].split(',')

    gd['file_types'] = gd['file_types'].split(',')

    gd['last_printed'] = ''
    if 'print':
        print( 'gd', gd )
        print( gd['paths'], gd['file_types'] )
        print( gd['paths'] )
    return gd





def get_list_of_img_data( gd ):
    img_paths = []

    for p in gd['paths']:
        for f in gd['file_types']:
            img_paths += sggo(p,'*.'+f)

    blank = zeros((gd['extent'],gd['extent'],3),np.uint8)

    gd['list_of_img_data'] = []
    gd['img_buffer'] = {}
    for p in img_paths:
        print('Loading',p)
        q = Path(p).resolve().as_posix()
        img = zimread(q)
        gd['img_buffer'][q] = img
        img = resize_to_extent( img, gd['extent'] )
        img_data = {
            'file':q,
            'extent':gd['extent'],
            'square_embeding':None,
            'corner_x':0,
            'corner_y':0,
            }

        h,w,d = shape(img)
        blank = 0 * blank + gd['padval']
        e2 = gd['extent']//2
        blank[
            e2-h//2 : e2-h//2+h,
            e2-w//2 : e2-w//2+w,
            :d,
        ] = img
        img_data['square_embeding'] = blank

        gd['list_of_img_data'].append( img_data )








def _mi( gd ):
    if 'fig' not in gd:
        gd['fig'] = figure('fig',facecolor="0.0")
    mi(gd['bkg_image'],'fig')
    gd['fig'].tight_layout(pad=0)
    spause()



def make_bkg_image( gd ):
    gd['cols'] = int(gd['rcratio']*sqrt(len(gd['list_of_img_data'])))
    padsize = gd['padsize']
    min_x = 10**9
    min_y = 10**9
    max_x = 0
    max_y = 0
    rows,cols = 0,0

    for I in gd['list_of_img_data']:
        I['corner_x'] = cols * (gd['extent'] + padsize)
        I['corner_y'] = rows * (gd['extent'] + padsize)
        min_x = min(I['corner_x'],min_x)
        min_y = min(I['corner_y'],min_y)
        max_x = max(I['corner_x']+gd['extent'],max_x)
        max_y = max(I['corner_y']+gd['extent'],max_y)
        if cols < gd['cols']-1:
            cols += 1
        else:
            rows += 1
            cols = 0

    bkg = zeros((max_y+2*padsize,max_x+2*padsize,3),np.uint8) + gd['padval']
    for I in gd['list_of_img_data']:
        bkg[
            I['corner_y']+padsize:I['corner_y']+padsize+gd['extent'],
            I['corner_x']+padsize:I['corner_x']+padsize+gd['extent'],:] =\
            I['square_embeding']

    gd['bkg_image'] = bkg
    _mi( gd )  




def handle_events(event):

    time.sleep(0.01) # needed to allow main tread time to run

    x, y, k = event.xdata, event.ydata, event.key
    
    if k == 'q':
        cv2.destroyAllWindows()
        CA()
        sys.exit()

    if x is None:
        return

    padsize = gd['padsize']

    if 'list_of_img_data' in gd:
        for I in gd['list_of_img_data']:
            if y >= I['corner_y']+padsize:
                if y <= I['corner_y']+padsize+gd['extent']:
                    if x >= I['corner_x']+padsize:
                        if x <= I['corner_x']+padsize+gd['extent']:
                            s = I['file'].replace(opjh(),'')
                            
                            if s != gd['last_printed']:
                                print('\n'+qtd(s))
                                gd['last_printed'] = s
                            img = resize_to_extent(
                                    gd['img_buffer'][I['file']],
                                    gd['extent2'],
                                )
                            q = zeros((gd['image_info_area_height'],shape(img)[1],3),np.uint8)
                            imgq = np.concatenate((img,q),axis=0) 
                            fontsize = 0.4
                            cv2.putText(
                                imgq,
                                pname(s)+'/',
                                (10,shape(imgq)[0]-30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                fontsize,
                                (150,150,150),
                                1,
                                cv2.LINE_AA
                            )
                            cv2.putText(
                                imgq,
                                fname(s),
                                (10,shape(imgq)[0]-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                fontsize,#.3,
                                (150,150,150),
                                1,
                                cv2.LINE_AA
                            )                                
                            mci(
                                imgq,
                                title='mci'
                            )
                            return



if __name__ == '__main__':
    gd = process_args( command_line_args )
    get_list_of_img_data( gd )
    make_bkg_image( gd )
    cid0 = gd['fig'].canvas.mpl_connect('key_press_event', handle_events)
    cid1 = gd['fig'].canvas.mpl_connect('button_press_event', handle_events)
    cid2 = gd['fig'].canvas.mpl_connect('motion_notify_event', handle_events)
    plt.pause(10**9)
    raw_input()

#EOF
