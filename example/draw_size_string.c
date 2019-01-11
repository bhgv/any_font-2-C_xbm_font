

uint16_t Paint_DrawString_XBM(uint16_t Xstart, uint16_t Ystart, const char *pString,
                         xbm_font* Font, uint16_t Color_Background, uint16_t Color_Foreground )
{
    uint16_t Xpoint = Xstart;
    uint16_t Ypoint = Ystart;
    int i = 0;
    char fstCh;

    if (Font == NULL)
        return 0;

    fstCh = Font[0].ascii;

    if (Xstart > WIDTH || Ystart > HEIGHT) {
        Debug("Paint_DrawString_XBM Input exceeds the normal display range\r\n");
        return 0;
    }

    while ( *pString != '\0') {
        if (*pString == '\n'){
            Xpoint = Xstart;
            Ypoint += Font[i].h;

            pString++;
            continue;
        }

        i = *pString - fstCh;
        if (i < 0){
            pString++;
            continue;
        }

#if 0
        //if X direction filled , reposition to(Xstart,Ypoint),Ypoint is Y direction plus the Height of the character
        if ((Xpoint + Font[i].w ) > Paint.Width ) {
            Xpoint = Xstart;
            Ypoint += Font[i].h;
        }

        // If the Y direction is full, reposition to(Xstart, Ystart)
        if ((Ypoint  + Font[i].h ) > Paint.Height ) {
            Xpoint = Xstart;
            Ypoint = Ystart;
        }
#endif

#ifdef COMPRESSED
        Paint_DrawCompressedXBM(Xpoint, Ypoint, *pString, Font, Color_Background, Color_Foreground);
#else
        Paint_DrawChar_XBM(Xpoint, Ypoint, *pString, Font, Color_Background, Color_Foreground);
#endif

        Xpoint += Font[i].w;

        pString++;
    }

    return Xpoint;
}


uint16_t Paint_GetDrawStringWidth_XBM(const char *pString, xbm_font* Font)
{
    uint16_t Xpoint = 0;
    int i = 0;
    char fstCh;

    if (Font == NULL)
        return 0;

    fstCh = Font[0].ascii;

    while ( *pString != '\0') {
        if (*pString == '\n'){
            Xpoint = 0;
            pString++;
            continue;
        }

        i = *pString - fstCh;
        if (i < 0){
            pString++;
            continue;
        }

        Xpoint += Font[i].w;

        pString++;
    }

    return Xpoint;
}
