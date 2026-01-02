import cv2
import numpy as np

class SmartBottleProcessor:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        self.win_name = "Color Morph V7 - Pro Object Lock"
        cv2.namedWindow(self.win_name)
        
        # Parametri stare
        self.track_point = None
        self.target_hue = None
        self.new_hue = 0   # Incepem cu Rosu de ex.
        self.tolerance = 15
        self.last_hull = None
        
        cv2.setMouseCallback(self.win_name, self.on_click)
        cv2.createTrackbar("Culoare Noua", self.win_name, self.new_hue, 179, self.nothing)
        cv2.createTrackbar("Sensibilitate", self.win_name, self.tolerance, 40, self.nothing)

    def nothing(self, x): pass

    def on_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.track_point = (x, y)
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                self.target_hue = hsv[y, x, 0]
                self.last_hull = None # Resetam memoria la click nou
                print(f"Obiect fixat! Hue detectat: {self.target_hue}")

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            output = frame.copy()

            if self.target_hue is not None:
                self.new_hue = cv2.getTrackbarPos("Culoare Noua", self.win_name)
                self.tolerance = cv2.getTrackbarPos("Sensibilitate", self.win_name)

                # 1. Masca de culoare cu prag de saturatie (ignoram gri-ul)
                lower = np.array([max(0, self.target_hue - self.tolerance), 60, 40])
                upper = np.array([min(179, self.target_hue + self.tolerance), 255, 255])
                mask = cv2.inRange(hsv, lower, upper)
                
                # 2. Operatii morfologice agresive pentru a uni bucatile sticlei
                kernel = np.ones((7,7), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.dilate(mask, kernel, iterations=1)

                # 3. Gasim contururi si folosim Convex Hull
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                target_cnt = None
                if contours:
                    # Gasim conturul cel mai mare care e aproape de punctul de click/vechea pozitie
                    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:3]
                    for cnt in contours:
                        if cv2.contourArea(cnt) > 1000:
                            if self.last_hull is None:
                                if cv2.pointPolygonTest(cnt, self.track_point, False) >= 0:
                                    target_cnt = cnt
                                    break
                            else:
                                target_cnt = cnt # Tracking simplificat pe cel mai mare obiect
                                break

                if target_cnt is not None:
                    # Cream "Invelisul Convex" - Acesta umple eticheta si reflexiile
                    hull = cv2.convexHull(target_cnt)
                    self.last_hull = hull
                    
                    obj_mask = np.zeros_like(mask)
                    cv2.drawContours(obj_mask, [hull], -1, 255, -1)
                    
                    # Blur la masca pentru margini fine (Anti-aliasing)
                    obj_mask = cv2.GaussianBlur(obj_mask, (15, 15), 0)
                    
                    # 4. Schimbare culoare inteligenta
                    # Formula: Mentinem S si V original pentru realism
                    # $$P_{new} = (H_{new}, S_{orig}, V_{orig})$$
                    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
                    
                    # Modificam doar canalul Hue unde masca este activa
                    normalized_mask = obj_mask.astype(np.float32) / 255.0
                    
                    # Aplicam noul Hue proportional cu masca
                    hue_channel = img_hsv[:,:,0]
                    hue_channel[obj_mask > 0] = self.new_hue
                    img_hsv[:,:,0] = hue_channel
                    
                    # Reconvertim in BGR
                    final_obj = cv2.cvtColor(img_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
                    
                    # Combinam originalul cu obiectul colorat folosind masca blurata
                    mask_3ch = cv2.merge([normalized_mask, normalized_mask, normalized_mask])
                    output = (frame * (1 - mask_3ch) + final_obj * mask_3ch).astype(np.uint8)

                cv2.imshow("Masca Procesata (Holes Filled)", obj_mask if 'obj_mask' in locals() else mask)

            else:
                cv2.putText(output, "CLICK PE STICLA PENTRU LOCK", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow(self.win_name, output)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): break
            if key == ord('r'): self.target_hue = None

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = SmartBottleProcessor(0)
    app.run()