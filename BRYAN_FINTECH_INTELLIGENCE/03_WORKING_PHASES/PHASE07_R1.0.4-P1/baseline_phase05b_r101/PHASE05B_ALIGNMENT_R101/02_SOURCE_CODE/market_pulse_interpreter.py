#!/usr/bin/env python3
"""
market_pulse_interpreter.py — Bryan FinTech Intelligence Phase 05B-R1.3
Market Pulse Interpretation, Change/Direction Calculation & Cross-Indicator Synthesis.

Rules:
1. All changes must be mathematically calculated from authenticated historical observations.
2. Missing previous values yield change = None and direction = UNKNOWN (never fabricated 0.00 or SIDEWAYS).
3. Structured 8-point analytical interpretation distinguishing FACT, INTERPRETATION, and FORECAST.
4. Cross-indicator synthesis covering monetary policy, banking liquidity, capital markets, and retail payments.
"""

from typing import Dict, Any, List, Optional


class MarketPulseInterpreter:
    """Calculates movements and generates structured analytical financial intelligence."""

    @staticmethod
    def calculate_movement(current_val: Optional[float], prev_val: Optional[float],
                           unit: str = "") -> Dict[str, Any]:
        """
        Calculates change and direction only when both observations are authenticated.
        If previous observation is missing, returns change = None and direction = 'UNKNOWN'.
        Never defaults to 0.00 or SIDEWAYS!
        """
        if current_val is None or prev_val is None:
            return {
                "change": None,
                "direction": "UNKNOWN",
                "changeDescription": "Không có số liệu kỳ trước để tính toán biến động."
            }

        diff = round(current_val - prev_val, 4)
        if diff > 0:
            direction = "UP"
            chg_str = f"+{diff:g}"
        elif diff < 0:
            direction = "DOWN"
            chg_str = f"{diff:g}"
        else:
            direction = "FLAT"
            chg_str = "0.00"

        return {
            "change": chg_str,
            "direction": direction,
            "previousValue": prev_val,
            "changeDescription": f"Biến động {chg_str} {unit} so với phiên trước ({prev_val} {unit})."
        }

    @classmethod
    def generate_indicator_interpretation(cls, ind: Dict[str, Any], prev_val: Optional[float] = None) -> Dict[str, Any]:
        """
        Generates structured 8-point financial interpretation strictly segregating
        FACT, INTERPRETATION, and FORECAST.
        """
        ind_id = ind.get("indicatorId")
        ind_name = ind.get("indicatorName")
        status = ind.get("verificationStatus")
        val = ind.get("actualValue")
        unit = ind.get("unit", "")
        obs_d = ind.get("observationDate") or ind.get("observationPeriod") or "N/A"

        # If unverified or missing
        if status != "VERIFIED" or val is None:
            return {
                "indicatorId": ind_id,
                "status": status,
                "summary": f"Chỉ số {ind_name} hiện chưa xác thực được nguồn tin chính thống ({ind.get('verificationNote')}).",
                "fact": "Không có số liệu xác thực từ nguồn chính thống trong kỳ báo cáo này.",
                "interpretation": "Cần tiếp tục theo dõi các kênh thông tin chính thức của cơ quan quản lý.",
                "forecast": "Chờ đợi công bố định kỳ tiếp theo."
            }

        val_float = float(val) if isinstance(val, (int, float)) or (isinstance(val, str) and val.replace(".", "").replace("-", "").isdigit()) else None

        # Calculate movement if prev_val is available
        movement = cls.calculate_movement(val_float, prev_val, unit)
        chg_desc = movement["changeDescription"]

        # 8-point assessment per indicator
        assessments = {
            "MP-01": {
                "what": f"Tỷ giá trung tâm USD/VND ghi nhận ở mức {val} {unit} cho ngày {obs_d}.",
                "fact": f"NHNN niêm yết tỷ giá trung tâm đạt {val} {unit}. {chg_desc}",
                "interpretation": "Tỷ giá trung tâm phản ánh định hướng điều hành ngoại hối của NHNN nhằm cân bằng mục tiêu kiểm soát lạm phát và hỗ trợ năng lực cạnh tranh xuất khẩu.",
                "implication": "Tác động trực tiếp đến biên độ giao dịch của các NHTM (+/-5%) và chi phí nhập khẩu nguyên nhiên vật liệu của doanh nghiệp.",
                "monitoring": "Theo dõi sát diễn biến chỉ số DXY, dòng vốn FII/FDI và can thiệp thị trường qua kênh bán ngoại tệ kỳ hạn của NHNN."
            },
            "MP-02": {
                "what": f"Lãi suất liên ngân hàng kỳ hạn qua đêm ghi nhận ở mức {val} {unit} cho ngày {obs_d}.",
                "fact": f"Lãi suất giao dịch bình quân qua đêm trên thị trường liên ngân hàng đạt {val} {unit}. {chg_desc}",
                "interpretation": "Mức lãi suất phản ánh trạng thái thanh khoản VND ngắn hạn trong hệ thống ngân hàng thương mại.",
                "implication": "Lãi suất qua đêm biến động ảnh hưởng đến chi phí tài trợ vốn ngắn hạn giữa các tổ chức tín dụng và áp lực tỷ giá.",
                "monitoring": "Theo dõi quy mô chào thầu OMO của NHNN và chênh lệch lãi suất VND - USD trên thị trường liên ngân hàng."
            },
            "MP-03": {
                "what": f"Lãi suất tiền gửi 12 tháng cao nhất ghi nhận ở mức {val} {unit} ({ind.get('bankName', 'NHTM')}).",
                "fact": f"Khảo sát biểu lãi suất 12 tháng niêm yết ghi nhận mức cao nhất {val} {unit} tại {ind.get('bankName')}. {chg_desc}",
                "interpretation": "Mặt bằng lãi suất huy động 12 tháng thể hiện nỗ lực thu hút tiền gửi trung dài hạn để đáp ứng nhu cầu tăng trưởng tín dụng và tỷ lệ vốn ngắn hạn cho vay trung dài hạn.",
                "implication": "Tác động đến chi phí vốn (COF) của hệ thống ngân hàng và quyết định phân bổ tài sản của người gửi tiền.",
                "monitoring": "Theo dõi xu hướng điều chỉnh biểu lãi suất tại nhóm ngân hàng Big 4 và các NHTM cổ phần quy mô lớn."
            },
            "MP-04": {
                "what": f"Chỉ số VN-Index đóng cửa tại {val} {unit} trong phiên ngày {obs_d}.",
                "fact": f"VN-Index chốt phiên tại {val} điểm. {chg_desc}",
                "interpretation": "Diễn biến chỉ số phản ánh tâm lý thị trường chứng khoán, dòng tiền luân chuyển giữa các nhóm ngành ngân hàng, bất động sản và xuất khẩu.",
                "implication": "Kênh huy động vốn qua thị trường cổ phiếu và tài sản ròng của nhà đầu tư cá nhân lẫn tổ chức.",
                "monitoring": "Theo dõi thanh khoản toàn thị trường và động thái mua/bán ròng của khối nhà đầu tư nước ngoài."
            },
            "MP-05": {
                "what": f"Tăng trưởng tín dụng toàn nền kinh tế ghi nhận đạt {val} {unit} ({obs_d}).",
                "fact": f"Dư nợ tín dụng toàn hệ thống đạt mức tăng trưởng {val}% theo công bố chính thức.",
                "interpretation": "Mức tăng trưởng phản ánh tốc độ hấp thụ vốn của các doanh nghiệp và hộ kinh doanh trong chu kỳ phục hồi kinh tế.",
                "implication": "Tạo xung lực cho tăng trưởng GDP nhưng đòi hỏi giám sát chặt chẽ chất lượng nợ để kiểm soát nợ xấu tiềm ẩn.",
                "monitoring": "Theo dõi tiến độ phân bổ chỉ tiêu tín dụng của NHNN và cơ cấu cho vay theo các lĩnh vực ưu tiên."
            },
            "MP-06": {
                "what": f"Sản lượng giao dịch qua mã VietQR đạt {val} {unit} ({obs_d}).",
                "fact": f"Khối lượng giao dịch qua hạ tầng mã thanh toán chuẩn quốc gia VietQR đạt {val} tỷ giao dịch độc lập.",
                "interpretation": "Sự mở rộng mạnh mẽ của thanh toán số bán lẻ và hành vi không dùng tiền mặt của người tiêu dùng tại điểm chấp nhận thanh toán (merchant).",
                "implication": "Thúc đẩy tài chính toàn diện, giảm chi phí lưu thông tiền mặt và mở rộng hệ sinh thái ngân hàng số/FinTech.",
                "monitoring": "Theo dõi sự phát triển thanh toán QR xuyên biên giới (cross-border QR) với Thái Lan, Campuchia và Trung Quốc."
            },
            "MP-07": {
                "what": f"Lượng khách du lịch quốc tế đến Việt Nam đạt {val} {unit} ({obs_d}).",
                "fact": f"Số liệu Tổng cục Thống kê ghi nhận {val} triệu lượt khách quốc tế đến Việt Nam.",
                "interpretation": "Phục hồi nguồn thu dịch vụ quốc tế, mang lại dòng ngoại tệ dồi dào hỗ trợ cán cân thanh toán tổng thể.",
                "implication": "Hưởng lợi lan tỏa cho ngành hàng không, dịch vụ lưu trú, ăn uống và tiêu dùng bán lẻ nội địa.",
                "monitoring": "Theo dõi lượng khách từ các thị trường trọng điểm Đông Bắc Á, châu Âu và chính sách thị thực nhập cảnh."
            },
            "MP-08": {
                "what": f"Nghiệp vụ thị trường mở OMO ghi nhận vị thế ròng {val} {unit} ({obs_d}).",
                "fact": f"Thanh khoản điều hành qua thị trường mở đạt giá trị ròng {val} tỷ VND. {chg_desc}",
                "interpretation": "NHNN chủ động điều tiết thanh khoản thông qua kênh mua kỳ hạn (bơm) hoặc phát hành tín phiếu (hút) để định hướng mặt bằng lãi suất tiền tệ.",
                "implication": "Cân bằng cung cầu tiền tệ ngắn hạn mà không gây xáo trộn đến định hướng chính sách tiền tệ trung dài hạn.",
                "monitoring": "Theo dõi khối lượng tín phiếu đáo hạn và lãi suất trúng thầu OMO qua các phiên giao dịch kế tiếp."
            }
        }

        spec = assessments.get(ind_id, {
            "what": f"Chỉ số {ind_name} đạt {val} {unit}.",
            "fact": f"Số liệu quan sát đạt {val} {unit}.",
            "interpretation": f"Đánh giá xu hướng của {ind_name}.",
            "implication": "Tác động đến thị trường tài chính.",
            "monitoring": "Theo dõi các cập nhật dữ liệu tiếp theo."
        })

        return {
            "indicatorId": ind_id,
            "status": status,
            "summary": spec["what"],
            "fact": spec["fact"],
            "interpretation": spec["interpretation"],
            "implication": spec["implication"],
            "monitoring": spec["monitoring"],
            "forecast": "Dự báo phụ thuộc vào các phiên công bố số liệu vĩ mô và quyết định điều hành tiếp theo."
        }

    @classmethod
    def synthesize_cross_indicators(cls, verified_indicators: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Cross-indicator macro-to-micro analysis connecting monetary policy,
        banking liquidity, capital markets, and digital payment rails.
        """
        ind_map = {ind["indicatorId"]: ind for ind in verified_indicators}

        fx_rate = ind_map.get("MP-01", {}).get("actualValue")
        ib_rate = ind_map.get("MP-02", {}).get("actualValue")
        dep_rate = ind_map.get("MP-03", {}).get("actualValue")
        vnindex = ind_map.get("MP-04", {}).get("actualValue")
        credit = ind_map.get("MP-05", {}).get("actualValue")
        vietqr = ind_map.get("MP-06", {}).get("actualValue")
        tourists = ind_map.get("MP-07", {}).get("actualValue")
        omo = ind_map.get("MP-08", {}).get("actualValue")

        macro_themes = []

        # 1. Monetary & Liquidity Axis (USD/VND + Overnight Rate + OMO)
        if fx_rate and ib_rate:
            macro_themes.append({
                "theme": "Điều hành Tỷ giá & Thanh khoản Hệ thống",
                "observation": f"Tỷ giá trung tâm neo ở {fx_rate} VND/USD trong khi lãi suất liên ngân hàng qua đêm ở mức {ib_rate}%/năm.",
                "analysis": "Cơ quan quản lý duy trì sự linh hoạt trong điều hành lãi suất ngắn hạn để hỗ trợ ổn định tỷ giá trước các biến động quốc tế."
            })

        # 2. Banking Funding & Credit Transmission (Deposit Rate + Credit Growth)
        if dep_rate and credit:
            macro_themes.append({
                "theme": "Chi phí Vốn & Tăng trưởng Tín dụng",
                "observation": f"Lãi suất huy động 12T cao nhất đạt {dep_rate}%/năm song hành cùng tăng trưởng tín dụng đạt {credit}%.",
                "analysis": "Hệ thống ngân hàng cân đối giữa chi phí vốn đầu vào và mục tiêu tăng trưởng tín dụng hỗ trợ sản xuất kinh doanh."
            })

        # 3. Capital Market Sentiment (VN-Index + Interest Rates)
        if vnindex and ib_rate:
            macro_themes.append({
                "theme": "Thị trường Vốn & Môi trường Lãi suất",
                "observation": f"VN-Index tại {vnindex} điểm trong bối cảnh mặt bằng lãi suất tiền tệ duy trì ở mức {ib_rate}%.",
                "analysis": "Định giá chứng khoán tiếp tục phản ánh kỳ vọng phục hồi lợi nhuận doanh nghiệp trong điều kiện chi phí vốn được kiểm soát hợp lý."
            })

        # 4. Digital Economy & Inbound Flow (VietQR + Tourism)
        if vietqr and tourists:
            macro_themes.append({
                "theme": "Kinh tế Số & Dòng tiền Khách Quốc tế",
                "observation": f"Sản lượng VietQR đạt {vietqr} tỷ giao dịch cùng với {tourists} triệu lượt khách quốc tế.",
                "analysis": "Sự cộng hưởng giữa hạ tầng thanh toán số mở rộng và dòng chi tiêu từ du lịch quốc tế hỗ trợ tích cực cho tổng mức bán lẻ."
            })

        return {
            "crossAnalysisTimestamp": ind_map.get("MP-01", {}).get("observationTimestamp"),
            "totalIndicatorsAnalyzed": len(verified_indicators),
            "macroThemes": macro_themes
        }
