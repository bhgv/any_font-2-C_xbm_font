
#include <stdio.h>
#include <stdint.h>

#include "z_049.xbm"


static uint16_t xp, yp;

uint16_t yo = 0;

static void __aux_Paint_DrawByteXBM(uint16_t x, uint16_t y, uint8_t b)
{
    uint8_t i;
    uint8_t clr;

        if(y != yo){
            printf("\ny=%d) ", y);
            yo = y;
        }

    for(i = 8; i > 0; i--){
        clr = (b & 1) == 0;
        //Paint_SetPixel(x, y, clr);
        printf(clr ? "0" : "_");

        x++;
        b >>= 1;
    }
}


static uint16_t __aux_Paint_DecompressDrawByteXBM(uint16_t x, uint16_t y,
                                              uint16_t w, uint16_t h,
                                              const uint8_t* xbm_buffer,
                                              uint16_t i,
                                              uint16_t a_xp[], uint8_t *a_xp_n)
{
    uint16_t j;
    uint8_t b = xbm_buffer[i];
    uint8_t n = b & (0x40 - 1);

    i++;

    switch(b & 0xC0){
    case 0x00:
        for(j = 0; j < n; j++){
            __aux_Paint_DrawByteXBM(x + xp, y + yp, 0);
            xp += 8;
            if(xp >= w){
                xp = 0;
                yp++;
            }
        }
        break;

    case 0x40:
        for(j = 0; j < n; j++){
            __aux_Paint_DrawByteXBM(x + xp, y + yp, 0xFF);
            xp += 8;
            if(xp >= w){
                xp = 0;
                yp++;
            }
        }
        break;

    case 0x80:
        if(*a_xp_n == 64){
            uint8_t idx;

            for(idx = 0; idx < 63; idx++)
                a_xp[idx] = a_xp[idx + 1];
            a_xp[63] = i - 1;
        }else{
            a_xp[*a_xp_n] = i - 1;
            (*a_xp_n)++;
        }

        for(j = 0; j < n; j++){
            b = xbm_buffer[i];
            i++;
            __aux_Paint_DrawByteXBM(x + xp, y + yp, b);
            xp += 8;
            if(xp >= w){
                xp = 0;
                yp++;
            }
        }
        break;

    case 0xC0:
        if(n <= *a_xp_n){
            uint16_t i_tmp = a_xp[n];

            b = xbm_buffer[i_tmp];
            i_tmp++;
            n = b & (0x40 - 1);
            for(j = 0; j < n; j++){
                b = xbm_buffer[i_tmp];
                i_tmp++;
                __aux_Paint_DrawByteXBM(x + xp, y + yp, b);
                xp += 8;
                if(xp >= w){
                    xp = 0;
                    yp++;
                }
            }
        }
        break;

    }
    return i;
}


void Paint_DrawCompressedXBM(uint16_t x, uint16_t y, uint16_t w, uint16_t h,
                         const uint8_t* xbm_buffer)
{
    uint16_t i;

    uint16_t a_xp[64];
    uint8_t  a_xp_n = 0;

    xp = 0; yp = 0;
    for(i = 0; xbm_buffer[i] != (uint8_t)0 && yp < h; ){
        i = __aux_Paint_DecompressDrawByteXBM(x, y, w, h, xbm_buffer, i, a_xp, &a_xp_n);
    }
}


int
main(){
    Paint_DrawCompressedXBM(0, 0, z_049_width, z_049_height, z_049_bits);
}
