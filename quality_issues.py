"""
Flask snippets for quality-issue recording and review.
Drop into your existing app — adjust import paths / db connection
helper (`get_db()`) and blueprint registration to match your project.
"""

import json
from database import CursorFromConnectionFromPool
from datetime import datetime
from flask import request, render_template, redirect, url_for
from flask_login import current_user  # you're already using this pattern


class QualityIssues:
    def __init__(self, issue_type_id, issue_name, default_origin):
        self.issue_type_id = issue_type_id
        self.issue_name = issue_name
        self.default_origin = default_origin

    # ------------------------------------------------------------------
    # 1. Called from inside your existing /submit_processing handler,
    #    right after each processing_detail row is inserted and you have
    #    its returned processing_detail_id.
    # ------------------------------------------------------------------
    @classmethod
    def save_quality_issues(cls, cur, processing_detail_id, processing_id, smpl_no,
                             issues_json, reported_by):
        """
        issues_json: the JSON string coming from the packet row's hidden
        'quality_issues_json' field, e.g.:
        [
          {"issue_type_id": 4, "origin": "process_defect",
           "position_unit": "sheet", "defect_start": 12, "defect_end": 15,
           "remarks": "burr on edge"}
        ]
        Empty string / '[]' / None -> no-op.

        affected_numbers / affected_wt are NOT taken from the client — they're
        derived here from the packet's own processed_numbers / processed_wt /
        input_length, so the operator only ever enters where the defect
        started and ended, never a weight.
        """
        if not issues_json:
            return
        issues = json.loads(issues_json)

        # pull the packet's own totals once, reuse for every issue on this row
        cur.execute(
            """
            SELECT processed_numbers, processed_wt, input_length
            FROM processing_detail
            WHERE processing_detail_id = %s
            """,
            (processing_detail_id,),
        )
        processed_numbers, processed_wt, input_length = cur.fetchone()

        for issue in issues:
            unit = issue["position_unit"]                    # 'sheet' or 'metre'
            start, end = issue["defect_start"], issue["defect_end"]

            if unit == "sheet":
                affected_numbers = end - start + 1
                per_unit_wt = processed_wt / processed_numbers if processed_numbers else 0
                affected_wt = affected_numbers * per_unit_wt
            else:  # 'metre' — slitting / narrow CTL, continuous coil length
                affected_numbers = None
                per_metre_wt = processed_wt / input_length if input_length else 0
                affected_wt = (end - start) * per_metre_wt

            cur.execute(
                """
                INSERT INTO quality_issue
                    (processing_detail_id, processing_id, smpl_no, issue_type_id,
                     origin, position_unit, defect_start, defect_end,
                     affected_numbers, affected_wt, reported_by, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    processing_detail_id,
                    processing_id,
                    smpl_no,
                    issue["issue_type_id"],
                    issue["origin"],
                    unit,
                    start,
                    end,
                    affected_numbers,
                    round(affected_wt, 4),
                    reported_by,
                    issue.get("remarks"),
                ),
            )

    @classmethod
    def get_quality_issue_list(cls):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("SELECT issue_type_id, issue_name FROM quality_issue_type WHERE active "
                           "ORDER BY issue_type_id")
            user_data = cursor.fetchall()
        return user_data

    @classmethod
    def get_quality_issues_by_smplno(cls, smpl_no):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("""
                    SELECT qi.processing_detail_id, qit.issue_name, qi.origin, qi.position_unit,
                           qi.defect_start, qi.defect_end, qi.affected_wt,
                           qi.status, qi.disposition, qi.remarks
                    FROM quality_issue qi
                    JOIN quality_issue_type qit ON qit.issue_type_id = qi.issue_type_id
                    WHERE qi.smpl_no = %s
                    ORDER BY qi.reported_at""", (smpl_no,))
            cols = [c.name for c in cursor.description]
            quality_issues_by_detail = {}
            for r in cursor.fetchall():
                row = dict(zip(cols, r))
                quality_issues_by_detail.setdefault(row["processing_detail_id"], []).append(row)
        return quality_issues_by_detail


    # Inside your existing submit_processing() view, the loop that inserts
    # each packet row would gain one line after the RETURNING fetch. Since
    # quality_issues_json is emitted once per row (default "[]" even with no
    # issue), it stays parallel to output_length/packet_name/etc. — zip by
    # index the same way you already do for the other packet fields:
    #
    #   output_length_lst      = request.form.getlist("output_length")
    #   quality_issues_json_lst = request.form.getlist("quality_issues_json")
    #
    #   for i, output_length in enumerate(output_length_lst):
    #       cur.execute("INSERT INTO processing_detail (...) VALUES (...) "
    #                   "RETURNING processing_detail_id", (...))
    #       processing_detail_id = cur.fetchone()[0]
    #       save_quality_issues(cur, processing_detail_id, processing_id, smpl_no,
    #                            quality_issues_json_lst[i],
    #                            current_user.username)


    # ------------------------------------------------------------------
    # 2. Quality Review screen — plant head applies disposition after
    #    talking to the customer.
    # ------------------------------------------------------------------
    '''
    
    
    @quality_bp.route("/quality_review/decide", methods=["POST"])
    def quality_review_decide():
        quality_issue_id = request.form["quality_issue_id"]
        disposition = request.form["disposition"]          # rejected / salvaged / accepted
        customer_feedback = request.form.get("customer_feedback", "")
    
        cur = get_db().cursor()
        cur.execute(
            """
            UPDATE quality_issue
            SET disposition = %s,
                customer_feedback = %s,
                status = 'decided',
                decided_by = %s,
                decided_at = %s
            WHERE quality_issue_id = %s
            """,
            (disposition, customer_feedback, current_user.username,
             datetime.now(), quality_issue_id),
        )
        get_db().commit()
        return redirect(url_for("quality.quality_review"))
    
    
    # ------------------------------------------------------------------
    # 3. Yield report endpoint (returns JSON; wire to your existing
    #    Excel-export pattern the same way you did for cost analysis)
    # ------------------------------------------------------------------
    @quality_bp.route("/yield_report")
    def yield_report():
        smpl_no = request.args.get("smpl_no")
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
    
        cur = get_db().cursor()
        cur.execute(
            """
            SELECT
                pd.smpl_no,
                i.customer,
                SUM(pd.processed_wt) AS output_wt,
                COALESCE(SUM(qi.affected_wt) FILTER (WHERE qi.disposition = 'rejected'), 0) AS rejected_wt,
                COALESCE(SUM(qi.affected_wt) FILTER (WHERE qi.disposition = 'salvaged'), 0) AS salvaged_wt,
                COALESCE(SUM(qi.affected_wt) FILTER (WHERE qi.status = 'pending_review'), 0) AS pending_wt
            FROM processing_detail pd
            JOIN incoming i ON i.smpl_no = pd.smpl_no
            LEFT JOIN quality_issue qi ON qi.processing_detail_id = pd.processing_detail_id
            WHERE (%(smpl_no)s IS NULL OR pd.smpl_no = %(smpl_no)s)
            GROUP BY pd.smpl_no, i.customer
            """,
            {"smpl_no": smpl_no},
        )
        cols = [c.name for c in cur.description]
        return {"rows": [dict(zip(cols, r)) for r in cur.fetchall()]}'''