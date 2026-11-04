---
doc_id: <% tp.system.prompt("Record ID (e.g., MR-2026-01, TRN-2026-01)") %>
title: <% tp.system.prompt("Record title") %>
doc_type: record
standard: <% tp.system.suggester(["ISO 13485:2016", "ISO 27001:2022", "both"], ["ISO 13485:2016", "ISO 27001:2022", "both"]) %>
clauses: [<% tp.system.prompt("Clause references") %>]
record_date: <% tp.date.now("YYYY-MM-DD") %>
author: 
tags: [qms, record]
related: []
---

# <% tp.frontmatter.title %>

**Record ID:** <% tp.frontmatter.doc_id %>
**Date:** <% tp.date.now("DD/MM/YYYY") %>
**Author:** 

## Record Content

[Content of the record]

## Attachments

- [List any attachments]

## Sign-off

**Completed by:** _________________________ **Date:** ___/___/______
**Reviewed by:** _________________________ **Date:** ___/___/______

## Corrections

> Records are made once and are not revised. If an entry above is wrong, leave it as it is and add a dated, attributed correction here.

| Date | By | Correction |
|------|----|-----------|
| | | |
