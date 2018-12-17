"""
DPS Pagination resource package.
Copyright (c) 2018 Qualcomm Technologies, Inc.
 All rights reserved.
 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
 disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
 disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
 products derived from this software without specific prior written permission.
 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
 TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""

class Pagination:
    """ Class to provide paginated view """

    @staticmethod
    def get_paginated_list(model_data, url, start, limit):
        from app import conf

        count = len(model_data)

        obj = {'start': start, 'limit': limit, 'count': count, 'Country_Code': conf['CC']}
        if start < 1 or start > count:
            return {}
        else:
            if count < start:
                return model_data

            if start == 1:
                obj['previous'] = ''
                limit_prev = -1
            else:
                limit_prev = ((start * limit) - limit - 1)
                start_prev = (limit_prev - limit) + 1
                obj['previous'] = url + '?start=%d&limit=%d' % (start_prev, limit_prev)

            # make next url
            if (start * limit) >= count:
                obj['next'] = ''
            else:
                start_next = (start * limit)
                limit_next = (start_next + limit) - 1
                if limit_next > count:
                    limit_next = count
                obj['next'] = url + '?start=%d&limit=%d' % (start_next, limit_next)

            # finally extract result according to bounds
            obj['cases'] = model_data[(limit_prev + 1):(limit_prev + limit + 1)]
            return obj
