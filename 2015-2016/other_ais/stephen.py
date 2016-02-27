#Stephen Xu, Anna Ye, Justin Lin

global oldx
global oldy
xs = []
ys = []
xs.append(0)
ys.append(0)

def pong_ai(paddle_frect, other_paddle_frect, ball_frect, table_size):
    #ONLY WORKS IF PADDLE IS ON THE RIGHT.
    global xs
    global ys
    x = ball_frect.pos[0] 
    y = ball_frect.pos[1]
    xs.append(x)
    ys.append(y)
    slope = 0
    totaly = 0
    leftovery = 0    
    numscreens = 0
    targetx = 0
    
    #While travelling leftwards and away from the paddle
    #Center the paddle
    #While travelling rightwards towards the paddle
    #Predict where it will go by taking the slope times remaining distance mod height
    #Use minimal movement to get there.
    
    #ON RIGHT SIDE
    if paddle_frect.pos[0] > table_size[0]/2:
        if xs[len(xs)-2] > x:
            #Moving  leftwards (away from paddle)
            #Centre the paddle
            if table_size[1]/2 > paddle_frect.pos[1]+paddle_frect.size[1]/2:
                return "down"
            elif table_size[1]/2 == paddle_frect.pos[1]+paddle_frect.size[1]/2:
                return
            else:
                return "up"
            
        elif xs[len(xs)-2] < x:
            #Moving rightwards (towards the paddle)
            if ys[len(ys)-2] > y:
                #MOVING UP: remember that the origin is in the top left corner
                slope = (ys[len(ys)-2]-y)/(x-xs[len(xs)-2])
                totaly = abs(y - (paddle_frect.pos[0]-x)*slope)
                leftovery = totaly % table_size[1]
                numscreens = (totaly - leftovery)/table_size[1]
                if numscreens % 2 == 0:
                    if leftovery > paddle_frect.pos[1] + 1 and leftovery < paddle_frect.pos[1] + paddle_frect.size[1] - 1:
                        return
                    if paddle_frect.pos[1] + 1 < leftovery:
                        return "down"
                    else: 
                        return "up"
                else:
                    if table_size[1] - leftovery > paddle_frect.pos[1] + 1 and table_size[1] - leftovery < paddle_frect.pos[1] + paddle_frect.size[1] - 1:
                        return
                    if paddle_frect.pos[1] + paddle_frect.size[1] - 1 > table_size[1] - leftovery:
                        return "up"
                    else: 
                        return "down"                
            elif ys[len(ys)-2] < y:
                #MOVING DOWN remember that the origin is in the top left corner
                slope = (y- ys[len(ys)-2])/(x-xs[len(xs)-2])
                totaly = y + (paddle_frect.pos[0]-x)*slope
                leftovery = totaly % table_size[1]
                numscreens = (totaly - leftovery)/table_size[1]
                if numscreens % 2 == 1:
                    if table_size[1] - leftovery > paddle_frect.pos[1] + 1 and table_size[1] - leftovery < paddle_frect.pos[1] + paddle_frect.size[1] - 1:
                        return
                    if paddle_frect.pos[1] + paddle_frect.size[1] - 1 > table_size[1] - leftovery:
                        return "up"
                    else: 
                        return "down"
                else:
                    if leftovery > paddle_frect.pos[1] + 1 and leftovery < paddle_frect.pos[1] + paddle_frect.size[1] - 1:
                        return
                    if paddle_frect.pos[1] + 1 < leftovery:
                        return "down"
                    else: 
                        return "up"    
    else:
        #ON LEFT SIDE
        if xs[len(xs)-2] > x:
             #Moving rightwards (away from paddle)
            if ys[len(ys)-2] > y:
                #MOVING UP: remember that the origin is in the top left corner
                slope = (ys[len(ys)-2]-y)/(x-xs[len(xs)-2])
                totaly = abs(y - (paddle_frect.pos[0]-x)*slope)
                leftovery = totaly % table_size[1]
                numscreens = (totaly - leftovery)/table_size[1]
                if numscreens % 2 == 0:                    
                    if leftovery > paddle_frect.pos[1] + 1 and leftovery < paddle_frect.pos[1] + paddle_frect.size[1] - 1:
                        return
                    if paddle_frect.pos[1] + 1 < leftovery:
                        return "down"
                    else: 
                        return "up"
                else:
                      
                    if table_size[1] - leftovery > paddle_frect.pos[1] + 1 and table_size[1] - leftovery < paddle_frect.pos[1] + paddle_frect.size[1] - 1:
                        return
                    if paddle_frect.pos[1] + paddle_frect.size[1] - 1> table_size[1] - leftovery:
                        return "up"
                    else: 
                        return "down"                

            elif ys[len(ys)-2] < y:
                #MOVING DOWN remember that the origin is in the top left corner
                slope = (y- ys[len(ys)-2])/(x-xs[len(xs)-2])
                totaly = y + (paddle_frect.pos[0]-x)*slope
                leftovery = totaly % table_size[1]
                numscreens = (totaly - leftovery)/table_size[1]
                if numscreens % 2 == 1:                    
                    if table_size[1] - leftovery > paddle_frect.pos[1] + 1 and table_size[1] - leftovery < paddle_frect.pos[1] + paddle_frect.size[1] - 1:
                        return
                    if paddle_frect.pos[1] + paddle_frect.size[1] - 1> table_size[1] - leftovery:
                        return "up"
                    else: 
                        return "down"

                else:
                    if leftovery > paddle_frect.pos[1] + 1 and leftovery < paddle_frect.pos[1] + paddle_frect.size[1] - 1:
                        return
                    if paddle_frect.pos[1] + 1 < leftovery:
                        return "down"
                    else: 
                        return "up"    

        elif xs[len(xs)-2] < x:
            #Moving  leftwards (towards the paddle)
            #Centre the paddle
            if table_size[1]/2 > paddle_frect.pos[1]+paddle_frect.size[1]/2:
                return "down"
            elif table_size[1]/2 == paddle_frect.pos[1]+paddle_frect.size[1]/2:
                return
            else:
                return "up"
                        
            
