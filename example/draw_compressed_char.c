

static void __aux_Paint_DrawByteXBM(uint16_t x, uint16_t y, uint8_t b)
{
    uint8_t i;
    uint8_t clr;

    for(i = 8; i > 0; i--){
        clr = (b & 1) == 0;
        Paint_SetPixel(x, y, clr);
        x++;
        b >>= 1;
    }
}


void Paint_DrawCompressedXBM(uint16_t x, uint16_t y, uint16_t w, uint16_t h,
                         const uint8_t* xbm_buffer)
{
    uint16_t i, j;
    uint8_t b, n;
    uint16_t xp, yp;

    xp = 0; yp = 0;
    for(i = 0; xbm_buffer[i] != 0; ){
        b = xbm_buffer[i];
        i++;
        n = b & (0x40 - 1);

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

        }
        if(yp >= h)
            break;
    }
}
