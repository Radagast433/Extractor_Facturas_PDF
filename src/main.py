# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 16:06:45 2026

@author: Emanuel
"""

import os
import time
import queue
import textwrap
import serial
import serial.tools.list_ports
from pathlib import Path
from tkinter import Tk, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pymupdf  # PyMuPDF

# Configuración
DESKTOP_PATH = Path.home() / "Desktop"
FACTURAS_PATH = DESKTOP_PATH / "Facturas"

# Crear carpeta si no existe
FACTURAS_PATH.mkdir(exist_ok=True)

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
            'Ä': 'A', 'Ë': 'E', 'Ï': 'I', 'Ö': 'O', 'Ü': 'U',
            'Ã': 'A'
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
        self.emiter_dict['Tipo de Venta'] = self.text[0][5].replace(' TIPO DE VENTA: ', '').replace('TIPO DE VENTA: ', '')

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

class PDFHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.pending_files = []
        self.batch_timer = None
        self.root = None
        self.monitor = None
        self.recently_added = set()  # Para evitar duplicados
        
    def set_references(self, root, monitor):
        """Establecer referencias al root y monitor"""
        self.root = root
        self.monitor = monitor
    
    def is_pdf_ready(self, file_path):
        """Verificar si el archivo PDF está completamente escrito"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                return False
            
            # Intentar abrir el archivo para verificar que no está bloqueado
            with open(file_path, 'rb') as f:
                # Leer los primeros bytes para verificar que es un PDF
                header = f.read(4)
                if header != b'%PDF':
                    return False
            
            # Intentar abrir con PyMuPDF para verificar que está completo
            try:
                doc = pymupdf.open(file_path)
                doc.close()
                return True
            except:
                return False
                
        except Exception:
            return False
    
    def add_pdf_file(self, file_path):
        """Agregar archivo PDF a la lista de pendientes"""
        file_name = os.path.basename(file_path)
        
        # Verificar si el archivo ya fue agregado recientemente
        if file_path in self.recently_added:
            return
        
        # Verificar si el archivo está listo
        if self.is_pdf_ready(file_path):
            if file_path not in self.pending_files:
                self.pending_files.append(file_path)
                self.recently_added.add(file_path)
                print(f"📄 Archivo PDF detectado: {file_name}")
                
                # Programar limpieza del registro de archivos recientes
                self.root.after(5000, lambda: self.recently_added.discard(file_path))
                
                # Cancelar timer anterior si existe
                if self.batch_timer:
                    self.root.after_cancel(self.batch_timer)
                    self.batch_timer = None
                
                # Programar nueva verificación en 1 segundo
                self.batch_timer = self.root.after(1500, self.process_batch)
        else:
            # Si el archivo no está listo, programar verificación más tarde
            self.root.after(500, lambda: self.retry_add_pdf(file_path))
    
    def retry_add_pdf(self, file_path):
        """Reintentar agregar archivo PDF después de un tiempo"""
        if file_path not in self.pending_files and os.path.exists(file_path):
            if self.is_pdf_ready(file_path):
                self.add_pdf_file(file_path)
    
    def on_created(self, event):
        """Manejar evento de creación de archivo"""
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            time.sleep(0.1)  # Pequeña pausa
            self.add_pdf_file(event.src_path)
    
    def on_modified(self, event):
        """Manejar evento de modificación de archivo"""
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            # Solo procesar si el archivo no está ya en pendientes
            if event.src_path not in self.pending_files:
                self.add_pdf_file(event.src_path)
    
    def on_moved(self, event):
        """Manejar evento de movimiento/renombrado de archivo"""
        if not event.is_directory and event.dest_path.lower().endswith('.pdf'):
            time.sleep(0.1)
            self.add_pdf_file(event.dest_path)
    
    def process_batch(self):
        """Procesar el lote de archivos acumulados"""
        self.batch_timer = None
        
        # Solo procesar si hay archivos pendientes y no se está procesando
        if self.pending_files and self.monitor and not self.monitor.processing:
            # Hacer copia de la lista actual para procesar
            current_batch = self.pending_files.copy()
            
            # Verificar que todos los archivos siguen existiendo
            valid_batch = [f for f in current_batch if os.path.exists(f)]
            
            # Si hay archivos, procesarlos
            if valid_batch:
                self.monitor.process_batch_files(valid_batch)

class FacturasMonitor:
    def __init__(self):
        self.file_queue = queue.Queue()
        self.processing = False
        self.root = Tk()
        self.root.withdraw()  # Ocultar ventana principal de tkinter
        
        # Inicializar observer
        self.event_handler = PDFHandler()
        self.event_handler.set_references(self.root, self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, str(FACTURAS_PATH), recursive=False)
        
        print(f"🔍 Monitoreando carpeta: {FACTURAS_PATH}")
        print("📂 Esperando nuevos archivos PDF...")
        print("=" * 50)
    
    def process_file(self, pdf_path):
        """Procesar un archivo PDF individual"""
        try:
            file_name = os.path.basename(pdf_path)
            print(f"🔄 Procesando: {file_name}")
            
            # Verificar que el archivo aún existe
            if not os.path.exists(pdf_path):
                print(f"⚠️ Archivo no encontrado: {file_name}")
                return
            
            # Crear instancia del extractor
            extractor = ExtractordeFacturas(pdf_path)
            
            # Imprimir los datos
            extractor.ImprimirDatos()
            
            print(f"✅ Procesado exitosamente: {file_name}")
            
        except Exception as e:
            print(f"❌ Error procesando {os.path.basename(pdf_path)}: {str(e)}")
    
    def process_batch_files(self, batch_files):
        """Procesar un lote de archivos"""
        if not batch_files or self.processing:
            return
            
        file_count = len(batch_files)
        file_names = [os.path.basename(f) for f in batch_files]
        
        print(f"📊 Lote listo para procesar: {file_count} archivo(s)")
        
        # Preguntar al usuario
        if self.ask_process_files(file_count, file_names):
            print("▶️ Iniciando procesamiento del lote...")
            self.processing = True
            
            # Procesar todos los archivos del lote
            for pdf_path in batch_files:
                self.process_file(pdf_path)
                time.sleep(0.5)  # Pausa entre archivos
                
                # Remover del pending_files si aún está allí
                if pdf_path in self.event_handler.pending_files:
                    self.event_handler.pending_files.remove(pdf_path)
            
            print("✅ Procesamiento del lote completado")
            print("-" * 50)
            self.processing = False
        else:
            print("⏸️ Procesamiento del lote cancelado por el usuario")
            print("-" * 50)
            # Remover los archivos del lote de pending_files
            for pdf_path in batch_files:
                if pdf_path in self.event_handler.pending_files:
                    self.event_handler.pending_files.remove(pdf_path)
    
    def ask_process_files(self, file_count, file_names):
        """Preguntar al usuario si desea procesar los archivos"""
        # Traer la ventana al frente
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        self.root.lift()
        
        # Crear lista de todos los nombres de archivos
        all_files = "\n".join([f"• {name}" for name in file_names])
        
        respuesta = messagebox.askyesno(
            "Nuevos archivos detectados",
            f"Se han detectado {file_count} nuevo(s) archivo(s) PDF:\n\n{all_files}\n\n¿Desea procesarlos ahora?"
        )
        
        # Restaurar atributo
        self.root.attributes('-topmost', False)
        
        return respuesta
    
    def start(self):
        """Iniciar el monitor"""
        # Iniciar observer
        self.observer.start()
        
        try:
            print("🚀 Monitor iniciado. Presiona Ctrl+C para detener.")
            print("=" * 50)
            
            # Mantener la aplicación corriendo
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            self.stop()
    
    def stop(self):
        """Detener el monitor"""
        self.observer.stop()
        self.observer.join()
        print("\n🛑 Monitor detenido")

if __name__ == "__main__":
    print("🚀 Iniciando Monitor de Facturas PDF")
    print("=" * 50)
    
    monitor = FacturasMonitor()
    
    try:
        monitor.start()
    except Exception as e:
        print(f"❌ Error al iniciar: {e}")