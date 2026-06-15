import math
import os
p = pow(2,255) - 19
A = 486662
G_X = 9

#the y axis isnt needed yet, since if we have the x coordinate
#we can just calc the y coordinate

#y^3 = x^3 + 486662x^2 + x

print(p)

def double_and_add(Secret, Start):
    x_2,z_2,x_3,z_3 = 1,0,Start,1
    prev_bit = 0
    for i in range(254,-1,-1):
        current_bit = (Secret >> i ) & 1
        swap_condition = current_bit ^ prev_bit
        mask = -swap_condition
        dummy_x = mask & (x_2 ^ x_3)
        dummy_z = mask & (z_2 ^ z_3)
        x_2 = x_2 ^ dummy_x
        x_3 = x_3 ^ dummy_x
        z_2 = z_2 ^ dummy_z
        z_3 = z_3 ^ dummy_z
        u,v,w,t = (x_2 - z_2) % p, #u
        (x_2 + z_2) % p,  #v
        (x_3 - z_3) % p,  #w
        (x_3 + z_3) % p #t
        uu,vv,wt,tu = (u * u) % p, #uu
        (v * v) % p, #vv
        (w * t) % p, #wv
        (t * u) % p  #tu
        x_2,z_2,x_3,z_3 = (uu * vv) % p, #x_2
        ((vv - uu) * (uu + (A * (vv - uu)//4))) % p, #z_2
        pow(wt + tu,2) % p, #x_3
        Start * pow(wt - tu,2) % p #z_3
        dummy_x = mask & (x_2 ^ x_3)
        dummy_z = mask & (z_2 ^ z_3)
        x_2 = x_2 ^ dummy_x
        x_3 = x_3 ^ dummy_x
        z_2 = z_2 ^ dummy_z
        z_3 = z_3 ^ dummy_z
        prev_bit = current_bit
    dummy_x = mask & (x_2 ^ x_3)
    dummy_z = mask & (z_2 ^ z_3)
    x_2 = x_2 ^ dummy_x
    x_3 = x_3 ^ dummy_x
    z_2 = z_2 ^ dummy_z
    z_3 = z_3 ^ dummy_z
    Final_x = (x_2 * pow(z_2,p - 2)) % p
    return Final_x

