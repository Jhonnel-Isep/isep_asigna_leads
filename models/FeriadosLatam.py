import datetime
import calendar


class FeriadosLatam:
    # Constantes
    x = datetime.datetime.now()
    year = x.year  # para automatico x.year , manual colocar año
    # Computus
    A = year % 19
    B, C = divmod(year, 100)
    D, E = divmod(B, 4)
    F = (B + 8) // 25
    G = (B - F + 1) // 3
    H = (19 * A + B - D - G + 15) % 30
    I, K = divmod(C, 4)
    L = (32 + 2 * E + 2 * I - H - K) % 7
    M = (A + 11 * H + 22 * L) // 451
    N = H + L - 7 * M + 114
    month = N // 31
    day = 1 + (N % 31)
    # Dias feriado fijos
    easter = datetime.date(year, month, day)
    miercoles_ceniza = easter - datetime.timedelta(days=46)
    martes_carnaval = easter - datetime.timedelta(days=47)
    lunes_carnaval = easter - datetime.timedelta(days=48)
    reyes = datetime.date(year, 1, 6)
    san_jose = datetime.date(year, 3, 19)
    jueves_santo = easter - datetime.timedelta(days=3)
    viernes_santo = easter - datetime.timedelta(days=2)
    sabado_santo = easter - datetime.timedelta(days=1)
    palm_sunday = easter - datetime.timedelta(days=7)
    dia_ascension = easter + datetime.timedelta(days=39)
    corpus_christi = easter + datetime.timedelta(days=60)
    sagrado_corazon = easter + datetime.timedelta(days=71)
    san_pedro_pablo = datetime.date(year, 6, 29)
    asuncion_virgen = datetime.date(year, 8, 15)
    dia_raza = datetime.date(year, 10, 12)
    dia_tsantos = datetime.date(year, 11, 1)
    dia_americas = datetime.date(year, 4, 14)

    # Funciones
    def siguiente_lunes(self, dia):  # Calcula el Lunes siguiente del dia feriado
        faa = 6
        dif = 0

        for foo in range(1, 7):
            if dia == calendar.day_name[foo]:
                dif = faa
                break
            else:
                faa -= 1

        return dif

    def anterior_lunes(self, dia):  # Calcula el Lunes anterior del dia feriado
        faa = -6
        dif = 0

        for foo in range(1, 7):
            if dia == calendar.day_name[foo]:
                dif = faa
                break
            else:
                faa += 1

        return dif

    def dinamico_colombia(self, dia):  # Tambien funciona para casos de Honduras
        d_name = str(dia.strftime("%A"))
        if d_name != "Monday":
            res = dia + datetime.timedelta(days=self.siguiente_lunes(d_name))
            return res
        else:
            return dia

    def dinamico_mexico(self, dia):
        d_name = str(dia.strftime("%A"))
        if d_name != "Monday":
            res = dia + datetime.timedelta(days=self.anterior_lunes(d_name))
            return res
        else:
            return dia

    def date_format(self, date):
        split = str(date).split("-")
        mes = split[1]
        dia = split[2]
        fecha = (int(split[1]), int(split[2]))
        return fecha

    # Calculo de feriado
    def mexico(self):
        constitucion_m = datetime.date(self.year, 2, 1)
        natalicio_benito = datetime.date(self.year, 3, 15)
        dia_revolucion = datetime.date(self.year, 11, 15)
        c_mex = self.date_format(self.dinamico_mexico(constitucion_m))
        b_suar = self.date_format(self.dinamico_mexico(natalicio_benito))
        r_mex = self.date_format(self.dinamico_mexico(dia_revolucion))
        d_resu = self.date_format(self.easter)

        lista = [(1, 1), c_mex, b_suar, d_resu, (5, 1), (9, 16), r_mex, (12, 25)]
        return lista

    def colombia(self):
        r_mag = self.date_format(self.dinamico_colombia(self.reyes))
        s_jose = self.date_format(self.dinamico_colombia(self.san_jose))
        j_santo = self.date_format(self.jueves_santo)
        v_santo = self.date_format(self.viernes_santo)
        d_resu = self.date_format(self.easter)
        d_ascen = self.date_format(self.dinamico_colombia(self.dia_ascension))
        c_christi = self.date_format(self.dinamico_colombia(self.corpus_christi))
        s_corazon = self.date_format(self.dinamico_colombia(self.sagrado_corazon))
        s_pedro = self.date_format(self.dinamico_colombia(self.san_pedro_pablo))
        v_asun = self.date_format(self.dinamico_colombia(self.asuncion_virgen))
        d_ra = self.date_format(self.dinamico_colombia(self.dia_raza))
        d_santos = self.date_format(self.dinamico_colombia(self.dia_tsantos))
        indepen = self.date_format(
            self.dinamico_colombia(datetime.date(self.year, 11, 11))
        )
        lista = [
            (1, 1),
            r_mag,
            s_jose,
            j_santo,
            v_santo,
            d_resu,
            (5, 1),
            d_ascen,
            c_christi,
            s_corazon,
            s_pedro,
            (7, 20),
            (8, 7),
            v_asun,
            d_ra,
            d_santos,
            indepen,
            (12, 8),
            (12, 25),
        ]
        return lista

    def salvador(self):
        j_santo = self.date_format(self.jueves_santo)
        v_santo = self.date_format(self.viernes_santo)
        s_santo = self.date_format(self.sabado_santo)
        d_resu = self.date_format(self.easter)

        lista = [
            (1, 1),
            j_santo,
            v_santo,
            s_santo,
            d_resu,
            (5, 1),
            (5, 10),
            (6, 17),
            (8, 5),
            (8, 6),
            (9, 15),
            (11, 2),
            (12, 25),
        ]

        return lista

    def honduras(self):
        j_santo = self.date_format(self.jueves_santo)
        v_santo = self.date_format(self.viernes_santo)
        s_santo = self.date_format(self.sabado_santo)
        d_resu = self.date_format(self.easter)
        d_america = self.date_format(self.dinamico_colombia(self.dia_americas))
        d_ra = self.date_format(self.dinamico_colombia(self.dia_raza))
        d_fuer = self.date_format(
            self.dinamico_colombia(datetime.date(self.year, 10, 21))
        )

        lista = [
            (1, 1),
            j_santo,
            v_santo,
            s_santo,
            d_resu,
            d_america,
            (5, 1),
            (9, 15),
            (10, 3),
            d_ra,
            d_fuer,
            (12, 25),
        ]

        return lista

    def nicaragua(self):
        j_santo = self.date_format(self.jueves_santo)
        v_santo = self.date_format(self.viernes_santo)
        s_santo = self.date_format(self.sabado_santo)
        d_resu = self.date_format(self.easter)

        lista = [
            (1, 1),
            j_santo,
            v_santo,
            d_resu,
            (5, 1),
            (7, 19),
            (9, 14),
            (9, 15),
            (12, 8),
            (12, 25),
        ]

        return lista

    def venezuela(self):
        l_carna = self.date_format(self.lunes_carnaval)
        m_carna = self.date_format(self.martes_carnaval)
        j_santo = self.date_format(self.jueves_santo)
        v_santo = self.date_format(self.viernes_santo)
        s_santo = self.date_format(self.sabado_santo)
        d_resu = self.date_format(self.easter)

        lista = [
            (1, 1),
            l_carna,
            m_carna,
            j_santo,
            v_santo,
            d_resu,
            (4, 19),
            (5, 1),
            (6, 24),
            (7, 5),
            (7, 24),
            (10, 12),
            (12, 24),
            (12, 25),
            (12, 31),
        ]
        return lista
