import math
import os
p = pow(2,255) - 19
A = 486662
G_X = 9
a24 = 121665
#the y axis isnt needed yet, since if we have the x coordinate
#we can just calc the y coordinate

#y^3 = x^3 + 486662x^2 + x


def double_and_add(Secret, Start):
    Secret &= ~(7)
    Secret &= ~(1 << 255)
    Secret |= (1 << 254)
    x_2, z_2, x_3, z_3 = 1, 0, Start, 1
    prev_bit = 0
    for i in range(254, -1, -1):
        current_bit = (Secret >> i) & 1
        swap_condition = current_bit ^ prev_bit
        mask = -swap_condition
        
        dummy_x = mask & (x_2 ^ x_3)
        dummy_z = mask & (z_2 ^ z_3)
        x_2 = x_2 ^ dummy_x
        x_3 = x_3 ^ dummy_x
        z_2 = z_2 ^ dummy_z
        z_3 = z_3 ^ dummy_z
        
        u = (x_2 - z_2) % p
        v = (x_2 + z_2) % p
        w = (x_3 - z_3) % p
        t = (x_3 + z_3) % p
        
        uu = (u * u) % p
        vv = (v * v) % p
        wv = (w * v) % p
        tu = (t * u) % p
        
        x_2, z_2 = (uu * vv) % p, ((vv - uu) * (uu + (a24 * (vv - uu)))) % p
        x_3, z_3 = pow(wv + tu, 2) % p, Start * pow(wv - tu, 2) % p
        
        dummy_x = mask & (x_2 ^ x_3)
        dummy_z = mask & (z_2 ^ z_3)
        x_2 = x_2 ^ dummy_x
        x_3 = x_3 ^ dummy_x
        z_2 = z_2 ^ dummy_z
        z_3 = z_3 ^ dummy_z
        prev_bit = current_bit
    mask = -prev_bit
    dummy_x = mask & (x_2 ^ x_3)
    dummy_z = mask & (z_2 ^ z_3)
    x_2 = x_2 ^ dummy_x
    z_2 = z_2 ^ dummy_z

    Final_x = (x_2 * pow(z_2, p - 2, p)) % p
    print(f"The final x -> {Final_x}")
    return Final_x
