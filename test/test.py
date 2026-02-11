# -*- coding: utf-8 -*-
"""
Created on Sun Feb  8 20:53:13 2026

@author: Emanuel
"""

import pymupdf
import textwrap
import serial
import serial.tools.list_ports

class ExtractordeFacturas:
    def __init__(self, ruta_pdf):
        self.doc = pymupdf.open(ruta_pdf)
        self.text = []
        
        self.ExtraerTexto()
        
        self.bill_dict = {'R.U.T.': '',
                         'Tipo': '',
                         'Numero': '',
                         'Lugar': '',
                         'Fecha Emision': ''}
        
        self.emiter_dict = {'Emisor': '',
                           'Giro': '',
                           'Email': '',
                           'Telefono': '',
                           'Tipo de Venta': ''}
        
        self.receiver_dict = {'SENOR(ES)': '',
                            'R.U.T.': '',
                            'Giro': '',
                            'Direccion': '',
                            'Comuna': '',
                            'Ciudad': '',
                            'Contacto': '',
                            'Tipo de Compra': ''}
        
        self.product_dict = {'Codigo': '',
                            'Descripcion': '',
                            'Cantidad': '',
                            'Precio': '',
                            'Valor': ''}
        
        self.bill_footing_dict = {'Forma de Pago': '',
                                 'Monto Neto': '',
                                 'I.V.A. 19%': '',
                                 'Impuesto Adicional': '',
                                 'Total': ''}

        self.product_list = []
        
        self.ExtraerDatos()
        self.EstructurarDatos()
    
    def reemplazar_acentos_espanol(self, texto):

        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ü': 'u', 'Ü': 'U',
            'ñ': 'n', 'Ñ': 'N',
            'ç': 'c', 'Ç': 'C',
            '¿': '', '¡': '',
            'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
            'Ä': 'A', 'Ë': 'E', 'Ï': 'I', 'Ö': 'O', 'Ü': 'U'
        }
        
        resultado = []
        for caracter in texto:
            resultado.append(reemplazos.get(caracter, caracter))
        
        return ''.join(resultado)
    
    def ExtraerTexto(self):
        
        for page in self.doc:
            _formatted_text = self.reemplazar_acentos_espanol(page.get_text())
            self.text.append(_formatted_text.split('\n'))
    
    def dividir_con_textwrap(self, texto, max_caracteres=79):
        lineas = textwrap.wrap(texto, width=max_caracteres, break_long_words=False, replace_whitespace=False)
        if (len(lineas) > 1):
            for i in range(1, len(lineas)):
                lineas[i] = (' ' * (lineas[0].find(':') + 2)) + lineas[i]
        
        return '\n'.join(lineas) + '\n'
    
    def ExtraerDatos(self):
        self.ExtraerDatosFactura()
        self.ExtraerDatosEmisor()
        self.ExtraerDatosReceptor()
        self.ExtraerDatosProductos()
        self.ExtraerDatosTotales()
        
    def EstructurarDatos(self):
        print_array = []
        
        for _key in self.bill_dict:
            print_array.append(' ' + _key + ' : ' + self.bill_dict[_key] + '\n')
        
        print_array.append('\n')
        
        for _key in self.emiter_dict:
            print_array.append(self.dividir_con_textwrap(' ' + _key + ' : ' + self.emiter_dict[_key]))
        
        print_array.append('\n')
        
        for _key in self.receiver_dict:
            print_array.append(self.dividir_con_textwrap(' ' + _key + ' : ' + self.receiver_dict[_key]))
        
        print_array.append('\n')
        
        ############################################################
        
        list_headers_position = [2, 15, 37, 54, 69]
        _header_row = [' '] * 80
        
        for _product_header_index, _key in enumerate(self.product_dict):
            for _char_index in range(len(_key)):
                _header_row[list_headers_position[_product_header_index] + _char_index] = _key[_char_index]
        
        _header_row = '\n' + ''.join(_header_row)
        print_array.append(_header_row + '\n')
        
        for _product in self.product_list:
            _product_row = [' '] * 80
            for _product_info_index, _key in enumerate(_product):
                for _char_index in range(len(_product[_key])):
                    _product_row[list_headers_position[_product_info_index] + _char_index] = _product[_key][_char_index]
            
            _product_row[len(_product_row) - 1] = '\n'
            _product_row = ''.join(_product_row)
            print_array.append(_product_row)
            
        print_array.append('\n\n')
        
        #############################################################
        
        for _key in self.bill_footing_dict:
            if (_key == 'Forma de Pago'):
                print_array.append(' ' + _key + ' : ' + (' ' * (25 - len(_key))) + self.bill_footing_dict[_key] + '\n')
            else:
                print_array.append(' ' + _key + ' : ' + (' ' * (25 - len(_key))) + '$' + self.bill_footing_dict[_key] + '\n')
        
        print_array.append('\n' * 15)
        
        self.print_data = print_array
        #print(''.join(self.print_data))
    
    def ImprimirDatos(self):
        printer_port = ''
        printer_hwid = '00:12:f3:11:3b:96'
        printer_hwid = printer_hwid.replace(':', '')
        printer_hwid = printer_hwid.upper()
          
        myports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(myports):
            if (printer_hwid in hwid):
                printer_port = port
                break
        
        if (printer_port == ''):
            print("No se encontró la impresora")
            return
        
        printer_serial_port = None
        connection_baud = 15200
        
        try:
            printer_serial_port = serial.Serial("{}".format(printer_port), connection_baud, timeout=1)
            
            for row in self.print_data:
                printer_serial_port.write(row.encode('ascii'))
            
            print("Factura impresa exitosamente")
            
        except Exception as e:
            print(f"Error al imprimir: {e}")
        
        finally:
            if printer_serial_port and printer_serial_port.isOpen():
                printer_serial_port.close()
    
    def ExtraerDatosFactura(self):
        ####################### DATOS FACTURA #######################
        self.bill_dict['R.U.T.'] = self.text[0][self.text[0].index('FACTURA ELECTRONICA') - 1].replace('R.U.T.:', '')
        self.bill_dict['Tipo'] = self.text[0][self.text[0].index('FACTURA ELECTRONICA')]
        self.bill_dict['Numero'] = self.text[0][self.text[0].index('FACTURA ELECTRONICA') + 1].replace('º', ' ')
        self.bill_dict['Lugar'] = self.text[0][self.text[0].index('FACTURA ELECTRONICA') + 2]
        self.bill_dict['Fecha Emision'] = self.text[0][self.text[0].index('FACTURA ELECTRONICA') + 3].replace('Fecha Emision: ', '')
    
    def ExtraerDatosEmisor(self):
        ####################### DATOS EMISOR #######################     
        self.emiter_dict['Emisor'] = self.text[0][0]
        self.emiter_dict['Giro'] = self.text[0][1].replace(' Giro: ', '') + ' ' + self.text[0][2] + ' ' + self.text[0][3]
        self.emiter_dict['Email'] = self.text[0][4][8:self.text[0][4].find('Telefono') - 1]
        self.emiter_dict['Telefono'] = self.text[0][4][self.text[0][4].find('Telefono') + len('Telefono :'):]
        self.emiter_dict['Tipo de Venta'] = self.text[0][5].replace(' TIPO DE VENTA: ', '')

    def ExtraerDatosReceptor(self):
        ####################### DATOS RECEPTOR #######################
        
        _reciever_start_index = -1
        for i in range(len(self.text[0])):
            if ('SENOR(ES): ' in self.text[0][i]):
                _reciever_start_index = i
                break
        
        _receiver_name = ''
        
        for i in range(_reciever_start_index, len(self.text[0])):
            if ('R.U.T.:' in self.text[0][i]):
                break
            _receiver_name+= self.text[0][i]
            _receiver_name+= ' '
        
        _receiver_name = _receiver_name.replace('SENOR(ES): ', '')
        
        self.receiver_dict['SENOR(ES)'] = _receiver_name
        self.receiver_dict['R.U.T.'] = self.text[0][self.text[0].index('R.U.T.:') + 1]
        self.receiver_dict['Giro'] = self.text[0][self.text[0].index('R.U.T.:') + 3]
        self.receiver_dict['Direccion'] = self.text[0][self.text[0].index('R.U.T.:') + 4].replace('DIRECCION: ', '')
        self.receiver_dict['Comuna'] = self.text[0][self.text[0].index('R.U.T.:') + 6]
        self.receiver_dict['Ciudad'] = self.text[0][self.text[0].index('R.U.T.:') + 8]
        
        _reciever_contact_start_index = -1
        for i in range(len(self.text[0])):
            if ('CONTACTO:' in self.text[0][i]):
                _reciever_contact_start_index = i
                break
        
        if ('TIPO' not in self.text[0][_reciever_contact_start_index + 1]):
            self.receiver_dict['Contacto'] = self.text[0][_reciever_contact_start_index + 1]
            self.receiver_dict['Tipo de Compra'] = self.text[0][_reciever_contact_start_index + 4]
        else:
            self.receiver_dict['Contacto'] = ''
            self.receiver_dict['Tipo de Compra'] = self.text[0][_reciever_contact_start_index + 3]

    def ExtraerDatosProductos(self):
        ####################### DATOS PRODUCTOS #######################
        for i in range(self.text[0].index('Valor') + 1, self.text[0].index('Timbre Electronico SII') - 1, 5):  
            self.product_list.append({'Codigo': self.text[0][i],
                                     'Descripcion': self.text[0][i + 1],
                                     'Cantidad': self.text[0][i + 2],
                                     'Precio': self.text[0][i + 3],
                                     'Valor': self.text[0][i + 4]})
        
    def ExtraerDatosTotales(self):
        ####################### DATOS TOTALES #######################
        self.bill_footing_dict['Forma de Pago'] = self.text[0][self.text[0].index('Timbre Electronico SII') - 1].replace('Forma de Pago:', '')
        self.bill_footing_dict['Monto Neto'] = self.text[0][self.text[0].index('MONTO NETO') + 2]
        self.bill_footing_dict['I.V.A. 19%'] = self.text[0][self.text[0].index('I.V.A. 19%') + 2]
        self.bill_footing_dict['Impuesto Adicional'] = self.text[0][self.text[0].index('IMPUESTO ADICIONAL') + 2]
        self.bill_footing_dict['Total'] = self.text[0][self.text[0].index('TOTAL') + 2]
        
if __name__ == "__main__":
    
    Extractor = ExtractordeFacturas('factura.pdf')